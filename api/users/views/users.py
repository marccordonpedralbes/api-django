"""Users views."""
# Django
from operator import sub
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Django REST Framework
import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)
from api.users.permissions import IsAccountOwner

# Models
from api.users.models import User, UserLoginActivity

from djmoney.money import Money

# Serializers
from api.users.serializers import (
    UserLoginSerializer,
    UserModelSerializer,
    UserSignUpSerializer,
    AccountVerificationSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    ValidateChangeEmail,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    IsEmailAvailableSerializer,
    IsUsernameAvailableSerializer,
)

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

# Celery
from api.taskapp.tasks import send_confirmation_email, send_feedback_email

import os
import stripe
import json

# Utils
from api.utils import helpers

from datetime import timedelta
from django.utils import timezone
import environ
env = environ.Env()


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = User.objects.filter(account_deactivated=False, is_staff=False)
    serializer_class = UserModelSerializer
    lookup_field = 'id'
    filter_backends = (SearchFilter,  DjangoFilterBackend)
    search_fields = ('first_name', 'last_name', 'username')

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in [
            'signup',
            'login',
            'verify',
                'forget_password']:
            permissions = [AllowAny]
        elif self.action in ['update', 'delete', 'partial_update', 'change_password', 'change_email', 'destroy']:
            permissions = [IsAccountOwner, IsAuthenticated]

        else:
            permissions = []
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action in ['list', 'partial_update', 'retrieve']:
            return UserModelSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserModelSerializer

    def get_queryset(self):
       
        return User.objects.filter(account_deactivated=False, is_staff=False)

    # User destroy

    def perform_destroy(self, instance):
        instance.account_deactivated = True
        instance.save()


    @action(detail=False, methods=['post'])
    def is_email_available(self, request):
        """Check if email passed is correct."""
        serializer = IsEmailAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        email = serializer.data
        return Response(data=email, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'])
    def is_username_available(self, request):
        """Check if email passed is correct."""
        serializer = IsUsernameAvailableSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        return Response(data={"message": "This username is available"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def signup(self, request):

        serializer = UserSignUpSerializer(data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        user_serialized = UserModelSerializer(user).data
        data = {
            "user": user_serialized,
            "access_token": token
        }

        return Response(data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['get'])
    def send_verification_email(self, request):
        """Send the email confirmation."""
        if request.user.id:
            user = request.user
            send_confirmation_email(user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login."""

        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}

        )

        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()

        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token,
        }

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """User login."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def change_email(self, request):
        """Account verification."""
        serializer = ChangeEmailSerializer(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def validate_change_email(self, request):
        """Account verification."""
        serializer = ValidateChangeEmail(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        email = serializer.save()
        data = {'message': 'Email changed!', 'email': email}
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def forget_password(self, request):
        """User login."""
        serializer = ForgetPasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Account verification."""
        serializer = ResetPasswordSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Account verification."""
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Verified account!'}
        return Response(data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'])
    def get_user(self, request, *args, **kwargs):
        if request.user.id == None:
            return Response(status=404)

        data = {
            'user': UserModelSerializer(request.user, many=False).data,
        }

        return Response(data)



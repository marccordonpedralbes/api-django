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

# Models
from api.products.models import Product


# Serializers
from api.products.serializers import *
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

class ProductViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Product.objects.all()
    serializer_class = ProductModelSerializer
    lookup_field = 'id'
    filter_backends = (SearchFilter,  DjangoFilterBackend)
    search_fields = ('nombre')

    def get_serializer_class(self):
        return ProductModelSerializer

    def get_queryset(self):
        return Product.objects.all()
"""Users views."""
# Django REST Framework
import uuid

from rest_framework import viewsets, mixins
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework import status
# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)

# Models
from api.recipes.models import Recipe


# Serializers
from api.recipes.serializers import *
# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


class RecipeViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeModelSerializer
    lookup_field = 'id'
    filter_backends = (SearchFilter,  DjangoFilterBackend)
    search_fields = ('nombre')

    def get_serializer_class(self):
        return RecipeModelSerializer

    def get_queryset(self):
        return Recipe.objects.all()

    def create(self, request, *args, **kwargs):
        ingredientes = []
        if 'ingredientes' in request.data:
            ingredientes = request.data['ingredientes']
        serializer = RecipeModelSerializer(data=request.data, context={'ingredientes':ingredientes})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
"""Users views."""
# Django REST Framework
import uuid

from rest_framework import viewsets, mixins
from django.http import HttpResponse
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
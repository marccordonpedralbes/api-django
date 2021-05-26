"""Users serializers."""

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Sum

# Django REST Framework
from rest_framework import serializers

# Models
from api.recipes.models import Recipe

class RecipeModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Recipe
        fields = (
            'id',
            'nombre',
            'descripcion',
            'duracion',
            'dificultad',
            'ingredientes'
        )
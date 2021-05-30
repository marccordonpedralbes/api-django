"""Users serializers."""

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.fields import ListField

# Django REST Framework
from rest_framework import serializers
from api.products.models import Product
from api.products.serializers import ProductModelSerializer

# Models
from api.recipes.models import Recipe

class RecipeModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    ingredientes=serializers.SerializerMethodField(read_only=True)
    class Meta:
        """Meta class."""

        model = Recipe
        fields = (
            'id',
            'nombre',
            'descripcion',
            'duracion',
            'dificultad',
            'recipeUrl',
            'ingredientes',
        )
    
    def get_ingredientes(self, obj):
        return ProductModelSerializer(obj.ingredientes, many=True).data

    def create(self, validated_data):
        ingredientes = self.context['ingredientes']
        receta = Recipe.objects.create(**validated_data)
        for ingrediente in ingredientes:
            product = Product.objects.get(id=ingrediente)
            receta.ingredientes.add(product)
            receta.save()
        return receta

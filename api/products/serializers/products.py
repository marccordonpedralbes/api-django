"""Users serializers."""

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Sum

# Django REST Framework
from rest_framework import serializers

# Models
from api.products.models import Product

class ProductModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Product
        fields = (
            'id',
            'nombre',
            'descripcion',
            'departamento',
            'imgURL',
        )
from rest_framework import viewsets, mixins

# Models
from api.products.models import Product

# Serializers
from api.products.serializers import *

# Filters
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


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
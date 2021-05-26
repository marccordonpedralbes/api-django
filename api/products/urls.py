"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import products as product_views


router = DefaultRouter()
router.register(r'products', product_views.ProductViewSet, basename='products')
urlpatterns = [
    path('', include(router.urls))
]

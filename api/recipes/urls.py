"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import recipes as recipe_views


router = DefaultRouter()
router.register(r'recipes', recipe_views.RecipeViewSet, basename='recipes')
urlpatterns = [
    path('', include(router.urls))
]

"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.recipes.models import Recipe


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    """UserLoginActivity model admin."""
    list_display = ("id", "nombre")

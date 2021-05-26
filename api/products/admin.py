"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.products.models import Product


@admin.register(Product)
class Product(admin.ModelAdmin):
    """UserLoginActivity model admin."""
    list_display = ("id", "nombre")

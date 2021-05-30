from django.db import models
import uuid

from api.products.models import Product

class Recipe(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True, verbose_name='Uuid')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    descripcion = models.TextField(null=True, blank=True, verbose_name='Descripción')
    duracion = models.FloatField(null=True, blank=True, verbose_name='Duracion de la preparacion')
    dificultad = models.CharField(max_length=150, null=True, blank=True, verbose_name='Dificultad de la receta')
    recipeUrl = models.CharField(max_length=150, verbose_name='Url de la imagen')
    ingredientes = models.ManyToManyField('products.Product', blank=True, related_name='Ingredientes')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        db_table = 'recipes'
        ordering = ['id']

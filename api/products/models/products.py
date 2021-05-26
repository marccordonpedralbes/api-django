from django.db import models
import uuid

class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True, verbose_name='Uuid')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    descripcion = models.TextField(null=True, blank=True, verbose_name='Descripción')
    departamento = models.CharField(max_length=150, verbose_name='Departamento')
    imgUrl = models.CharField(max_length=150, verbose_name='Url de la imagen')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        db_table = 'products'
        ordering = ['id']

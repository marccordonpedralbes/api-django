# Generated by Django 3.0.3 on 2021-05-27 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_recipe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='recipe',
        ),
    ]
# Generated by Django 3.0.3 on 2021-05-27 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredientes',
        ),
    ]

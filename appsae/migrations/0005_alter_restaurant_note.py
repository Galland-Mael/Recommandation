# Generated by Django 4.1.2 on 2022-11-16 14:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsae', '0004_restaurant_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='note',
            field=models.FloatField(default=0, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)]),
        ),
    ]

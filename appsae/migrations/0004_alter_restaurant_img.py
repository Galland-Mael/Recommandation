# Generated by Django 4.1.2 on 2022-11-16 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsae', '0003_remove_imagerestaurant_product_avis_note_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='img',
            field=models.ManyToManyField(blank=True, to='appsae.imagerestaurant'),
        ),
    ]

# Generated by Django 4.1.2 on 2022-11-16 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsae', '0003_remove_imagerestaurant_product_avis_note_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='img',
            field=models.ManyToManyField(to='appsae.imagerestaurant'),
        ),
    ]

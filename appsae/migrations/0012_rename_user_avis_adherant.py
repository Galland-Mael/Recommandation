# Generated by Django 4.1.2 on 2022-11-22 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appsae', '0011_avis_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='avis',
            old_name='user',
            new_name='adherant',
        ),
    ]

# Generated by Django 3.2.13 on 2023-10-03 16:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventarisation', '0002_inventarisation_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventarisation',
            old_name='dateTime',
            new_name='date_time',
        ),
    ]

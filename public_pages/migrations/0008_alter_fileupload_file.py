# Generated by Django 3.2.22 on 2024-02-21 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_pages', '0007_alter_publicpage_limited_to_committees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='file',
            field=models.FileField(upload_to='.'),
        ),
    ]

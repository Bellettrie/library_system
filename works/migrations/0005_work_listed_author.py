# Generated by Django 3.0.4 on 2020-05-13 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0004_auto_20200510_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='listed_author',
            field=models.CharField(default='ZZZZZZ', max_length=64),
        ),
    ]
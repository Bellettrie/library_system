# Generated by Django 3.0.4 on 2020-08-06 09:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lendings', '0002_auto_20200806_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lending',
            name='last_mailed',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 23, 9, 37, 35, 462361)),
        ),
    ]

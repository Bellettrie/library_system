# Generated by Django 3.0.3 on 2020-03-20 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0005_auto_20200320_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='old_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]

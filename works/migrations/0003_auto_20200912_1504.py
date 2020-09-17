# Generated by Django 3.0.4 on 2020-09-12 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0002_auto_20200819_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='language',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='item',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='works.Location'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='work',
            name='language',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]

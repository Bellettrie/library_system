# Generated by Django 3.0.4 on 2020-07-30 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0002_auto_20200730_1459'),
        ('inventarisation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventarisation',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='works.Location'),
            preserve_default=False,
        ),
    ]
# Generated by Django 3.2.10 on 2022-03-07 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0009_auto_20210604_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipperiod',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

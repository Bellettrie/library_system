# Generated by Django 3.0.4 on 2020-07-30 13:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Committee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=64)),
                ('active_member_committee', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('addressLineOne', models.CharField(max_length=255)),
                ('addressLineTwo', models.CharField(max_length=255)),
                ('addressLineThree', models.CharField(blank=True, max_length=255)),
                ('addressLineFour', models.CharField(blank=True, max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=64)),
                ('student_number', models.CharField(max_length=32)),
                ('membership_type_old', models.CharField(max_length=32)),
                ('notes', models.TextField()),
                ('old_customer_type', models.CharField(blank=True, max_length=64, null=True)),
                ('old_id', models.IntegerField(blank=True, null=True)),
                ('is_anonymous_user', models.BooleanField(default=False)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('privacy_activities', models.BooleanField(default=False)),
                ('privacy_publications', models.BooleanField(default=False)),
                ('privacy_reunions', models.BooleanField(default=False)),
                ('privacy_reunion_end_date', models.DateField(auto_now=True)),
                ('committees', models.ManyToManyField(blank=True, to='members.Committee')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('committee_update', 'Can update committee')],
            },
        ),
    ]

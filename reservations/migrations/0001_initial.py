# Generated by Django 3.2.10 on 2022-05-02 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('works', '0001_initial'),
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserved_on', models.DateField()),
                ('reservation_end_date', models.DateField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='works.item')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='members.member')),
                ('reserved_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservation_action_by', to='members.member')),
            ],
        ),
    ]

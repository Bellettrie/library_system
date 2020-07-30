# Generated by Django 3.0.4 on 2020-07-30 13:32

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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserved_on', models.DateField()),
                ('reservation_end_date', models.DateField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='works.Item')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='members.Member')),
                ('reserved_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservation_action_by', to='members.Member')),
            ],
        ),
        migrations.CreateModel(
            name='Lending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lended_on', models.DateField()),
                ('times_extended', models.IntegerField(default=0)),
                ('last_extended', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('handed_in', models.BooleanField()),
                ('handed_in_on', models.DateField(blank=True, null=True)),
                ('handed_in_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='handed_in', to='members.Member')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='works.Item')),
                ('lended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lended_out', to='members.Member')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='members.Member')),
            ],
            options={
                'permissions': [('extend', 'Can extend lending'), ('extend_with_fine', 'Extend book even though it has a fine'), ('return', 'Return book')],
            },
        ),
    ]

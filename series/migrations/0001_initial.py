# Generated by Django 3.2.10 on 2022-05-02 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('works', '0001_initial'),
        ('creators', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeriesNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('display_number', models.CharField(blank=True, max_length=255)),
                ('old_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('seriesnode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='series.seriesnode')),
                ('book_code_sortable', models.CharField(blank=True, max_length=128)),
                ('language', models.CharField(blank=True, max_length=64)),
                ('article', models.CharField(blank=True, max_length=64, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('sub_title', models.CharField(blank=True, max_length=255, null=True)),
                ('original_language', models.CharField(blank=True, max_length=64, null=True)),
                ('original_article', models.CharField(blank=True, max_length=64, null=True)),
                ('original_title', models.CharField(blank=True, max_length=255, null=True)),
                ('original_subtitle', models.CharField(blank=True, max_length=255, null=True)),
                ('is_translated', models.BooleanField()),
                ('book_code', models.CharField(max_length=16)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='works.location')),
                ('location_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='creators.locationnumber')),
            ],
            options={
                'abstract': False,
            },
            bases=('series.seriesnode', models.Model),
        ),
        migrations.CreateModel(
            name='WorkInSeries',
            fields=[
                ('seriesnode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='series.seriesnode')),
                ('is_primary', models.BooleanField(default=True)),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='works.work')),
            ],
            bases=('series.seriesnode',),
        ),
        migrations.AddField(
            model_name='seriesnode',
            name='part_of_series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='part', to='series.series'),
        ),
        migrations.AlterUniqueTogether(
            name='seriesnode',
            unique_together={('number', 'part_of_series')},
        ),
        migrations.CreateModel(
            name='CreatorToSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(blank=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='creators.creator')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='creators.creatorrole')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='series.series')),
            ],
            options={
                'unique_together': {('creator', 'series', 'number')},
            },
        ),
    ]

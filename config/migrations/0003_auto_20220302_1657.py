# Generated by Django 3.2.10 on 2022-03-02 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_lendingsettings_item_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lendingsettings',
            old_name='borrow_money_active',
            new_name='borrow_money',
        ),
        migrations.RenameField(
            model_name='lendingsettings',
            old_name='borrow_money_inactive',
            new_name='extend_count',
        ),
        migrations.RenameField(
            model_name='lendingsettings',
            old_name='extend_count_active',
            new_name='max_count',
        ),
        migrations.RenameField(
            model_name='lendingsettings',
            old_name='extend_count_inactive',
            new_name='term',
        ),
        migrations.RemoveField(
            model_name='lendingsettings',
            name='max_count_active',
        ),
        migrations.RemoveField(
            model_name='lendingsettings',
            name='max_count_inactive',
        ),
        migrations.RemoveField(
            model_name='lendingsettings',
            name='term_for_active',
        ),
        migrations.RemoveField(
            model_name='lendingsettings',
            name='term_for_inactive',
        ),
        migrations.AddField(
            model_name='lendingsettings',
            name='member_is_active',
            field=models.BooleanField(default=False),
        ),
    ]

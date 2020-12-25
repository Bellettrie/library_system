from django.db import migrations, models

from members.management.commands.add_member_start_dates import mig


def forwards(apps, schema_editor):
    if schema_editor.connection.alias != 'default':
        return
    from django.conf import settings
    if not settings.SHOULD_MIGRATE:
        return
    mig()
    # Your migration code goes here


class Migration(migrations.Migration):
    dependencies = [
        # Dependencies to other migrations
        ('members', '0006_auto_20201224_1304')
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='is_anonimysed',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(forwards),
    ]

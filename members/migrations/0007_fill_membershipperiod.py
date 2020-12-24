from django.db import migrations

from members.management.commands.add_member_start_dates import mig


def forwards(apps, schema_editor):
    if schema_editor.connection.alias != 'default':
        return
    mig()
    # Your migration code goes here


class Migration(migrations.Migration):
    dependencies = [
        # Dependencies to other migrations
        ('members', '0006_auto_20201224_1304')
    ]

    operations = [
        migrations.RunPython(forwards),
    ]

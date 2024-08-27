# Manually created migration.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book_code_generation', '0002_locationcuttercoderange'),
        ('creators', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='creatorlocationnumber',
            name='locationcuttercoderange_ptr',
            field=models.OneToOneField(
                auto_created=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                serialize=False,
                to='book_code_generation.locationcuttercoderange'),
            preserve_default=False,
        ),
        migrations.RunSQL("""
        UPDATE creators_creatorlocationnumber SET locationcuttercoderange_ptr_id = locationnumber_ptr_id;
        """),
        migrations.RemoveField(model_name='creatorlocationnumber', name='locationnumber_ptr'),

        migrations.AlterField(
            model_name='creatorlocationnumber',
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                serialize=False,
                to='book_code_generation.locationcuttercoderange',
                primary_key=True
            ),
            name='locationcuttercoderange_ptr'
        ),
    ]

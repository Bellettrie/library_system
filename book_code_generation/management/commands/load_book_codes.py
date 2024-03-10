from django.core.management.base import BaseCommand

from book_code_generation.location_number_creation import CutterCodeRange


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from bellettrie_library_system.settings_migration import migration_database
        mycursor = migration_database.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM cutter")
        CutterCodeRange.objects.all().delete()
        for x in mycursor:
            print(x)
            CutterCodeRange.objects.create(from_affix=x.get("begin").replace(" ", ""), to_affix=x.get("einde").replace(" ", ""), number=x.get("nummer"), generated_affix=x.get("combinatie").replace(" ", ""))

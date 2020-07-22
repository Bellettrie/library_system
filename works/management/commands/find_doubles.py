import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from bellettrie_library_system.settings_migration import migration_database
        mycursor = migration_database.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM band where signatuur like '%H-88-l%'")
        for x in mycursor:
            print(x)

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from members.models import Member, MembershipType, MemberBackground


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

        mycursor.execute("SELECT * FROM klant")

        for x in mycursor:
            z = Member.objects.filter(old_id=x.get("klantnummer"))
            if len(z) == 1:
                try:
                    m = MemberBackground.objects.get(old_str=x.get("herkomst"))
                    z[0].member_background = m
                except MemberBackground.DoesNotExist:
                    print(x.get("herkomst"))
                try:
                    m = MembershipType.objects.get(old_str=x.get("lidsoort"))
                    z[0].membership_type = m
                except MembershipType.DoesNotExist:
                    print(x.get("lidsoort"))
                try:
                    z[0].save()
                except ValueError:
                    print("ERROR")

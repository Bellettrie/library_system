import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_PWD, OLD_USN

from works.models import Creator


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

        persons = dict()

        mycursor.execute("SELECT * FROM persoon")

        for x in mycursor:
            persons[x.get("persoonnummer")] = x

        creators = dict()
        for p in persons.keys():
            old_id = persons.get(p).get("persoonnummer")
            comment = persons.get(p).get("commentaar")
            creator = Creator.objects.create(name=persons.get(p).get("naam"), given_names=persons.get(p).get("voornaam"), old_id=old_id, comment=comment)
            creators[old_id] = creator

        for p in persons.keys():
            connect_to = creators.get(persons.get(p).get("verwijzing"))
            if connect_to != 0:
                me = creators.get(persons.get(p).get("persoonnummer"))
                me.is_alias_of = connect_to
                me.save()

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from series.models import Series
from works.management.commands.load_works_from_db import fill_name


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @staticmethod
    def handle_series_node(node, tree, finder):
        data = finder.get(node)
        series = Series.objects.get(old_id=node)
        fill_name(series, data)
        series.save()

    def handle(self, *args, **options):
        from bellettrie_library_system.settings_migration import migration_database
        mycursor = migration_database.cursor(dictionary=True)

        tree = dict()
        finder = dict()
        mycursor.execute("SELECT * FROM publicatie where verbergen = 0")

        count = 0
        for x in mycursor:
            if x.get("reeks_publicatienummer") > 0:
                tree[x.get("publicatienummer")] = x.get("reeks_publicatienummer")
                count += 1
            finder[x.get("publicatienummer")] = x

        for t in finder.keys():
            if finder.get(t).get("type") == 1:
                Command.handle_series_node(t, tree, finder)

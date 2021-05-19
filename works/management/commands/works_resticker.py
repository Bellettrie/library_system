
from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_PWD, OLD_USN
from works.models import Item, Category, ItemType, Location, Creator


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for item in Item.objects.all():
            item.book_code_sortable="a"
            item.save()

from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import generate_code_from_author_translated


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from book_code_generation.models import get_number_for_code, generate_code_from_author
        from creators.models import Creator, CreatorLocationNumber

        from works.models import Item, CreatorToWork

        creators = Creator.objects.filter(name__icontains="Tolkien")
        creator = creators[1]

        works = CreatorToWork.objects.filter(creator=creator)
        work = works[0].work

        items = Item.objects.filter(publication=work)
        item = items[0]

        print(generate_code_from_author_translated(item))

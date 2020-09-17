from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code
from creators.models import Creator, CreatorLocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from works.models import Item, Location


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        total_collisions = 0
        error_books = 0
        items = Item.objects.all()

        author_to_item = dict()
        for item in items:
            authors = item.publication.get_authors()
            if len(authors) > 0:
                crea = authors[0].creator
                if len(CreatorLocationNumber.objects.filter(creator=crea, location=item.location)) > 0:
                    itemz = author_to_item.get(crea, [])
                    itemz.append(item)
                    author_to_item[crea] = itemz
        for location in Location.objects.filter(sig_gen='author'):
            cls = CreatorLocationNumber.objects.filter(location=location)
            number_dict = dict()
            for cl in cls:
                lst = number_dict.get((cl.number, cl.letter), [])
                lst.append(cl.creator)
                number_dict[(cl.number, cl.letter)] = lst
            for d in number_dict.keys():
                lst = number_dict[d]
                if len(lst) > 1:
                    strs = location.name + ":" + str(d)
                    lowest_count = 0
                    lowest_author = None

                    for item in lst:
                        current_count = len(author_to_item[item])
                        lowest_count = max(current_count, lowest_count)
                        if lowest_count == current_count:
                            lowest_author = item
                        error_books += current_count
                        strs += ";" + item.name
                    for item in lst:
                        if item is not lowest_author:
                            item.mark_for_change = True
                            item.save()
                    strs += "--" + str(lowest_author)
                    print(strs)
                    error_books -= lowest_count
                    total_collisions += 1
        print(total_collisions)
        print(error_books)

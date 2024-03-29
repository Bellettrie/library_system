from django.core.management.base import BaseCommand

from works.models import Item, Publication


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        authors = set()
        codes = dict()

        for pub in Publication.objects.all():
            if pub.listed_author not in authors:
                if len(pub.get_authors()) > 0:
                    for item in Item.objects.filter(publication=pub):
                        code = item.generate_code_prefix()
                        codes[code] = codes.get(code, [])

                        codes[code].append(pub.get_authors()[0].creator)
                        authors.add(pub.listed_author)
                        break

        for code in codes.keys():
            if code == "T-370":
                print(codes[code])
            if len(codes[code]) > 1:
                cre = codes[code][0]
                va = True
                for c in codes[code]:
                    if not (cre == c or c.is_alias_of == cre or cre.is_alias_of == c or cre.is_alias_of == c.is_alias_of):
                        va = False
                if not va:
                    print(code, codes[code])

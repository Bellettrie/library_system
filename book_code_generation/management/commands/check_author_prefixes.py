from django.core.management.base import BaseCommand

from book_code_generation.location_number_creation import CutterCodeRange
from works.models import Item


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        cutter = CutterCodeRange.get_cutter_number("Pratchett")
        print(cutter.generated_affix)
        items = Item.objects.filter(location__sig_gen__contains="author")
        wrongs = 0
        for item in items:
            sig = item.generate_code_prefix()

            sigs = (sig or "").split("-")

            cut = item.book_code.split("-")
            if cut[1] == "ABC":
                continue
            if sigs[0] != cut[0]:
                print("wrong first part: ", str(sigs), str(cut), item.publication.listed_author, item.old_id)
                wrongs += 1

            if len(sigs) > 1 and sigs[1] != cut[1]:
                print("wrong snd part: ", str(sigs), str(cut), item.publication.listed_author, item.old_id)
                wrongs += 1

            if len(sigs) > 2 and sigs[2] != cut[2]:
                print("wrong third part: ", str(sigs), str(cut), item.publication.listed_author, item.old_id)
                wrongs += 1

        print(wrongs)

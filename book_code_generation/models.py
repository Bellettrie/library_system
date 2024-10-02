from django.db import models

from book_code_generation.helpers import normalize_str, standardize_code

from creators.models import CreatorLocationNumber, LocationNumber


class CutterCodeResult:
    def __init__(self, name: str, number: int, is_from_cutter_table=False):
        self.name = normalize_str(name)
        self.number = number
        self.is_from_cutter_table = is_from_cutter_table

    def __str__(self):
        return self.name + "::" + str(self.number)


# Used to mock an item to run through the code, in case the item does not exist yet. Only contains the required fields for the item.
class FakeItem:
    def __init__(self, publication, location):
        self.publication = publication
        self.location = location


class CutterCodeRange(models.Model):
    from_affix = models.CharField(max_length=16)
    to_affix = models.CharField(max_length=16)
    number = models.CharField(max_length=16)
    generated_affix = models.CharField(max_length=20)

    @staticmethod
    def get_cutter_number(name: str, location=None):
        cutters = CutterCodeRange.objects.all().order_by("from_affix")

        result = None
        for cutter in cutters:
            if result is None:
                result = cutter
            if normalize_str(name) < cutter.from_affix:
                return result
            result = cutter
        return result


class BookCode(models.Model):
    class Meta:
        abstract = True

    book_code = models.CharField(max_length=64, blank=True)
    book_code_sortable = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        self.book_code_sortable = standardize_code(self.book_code)
        super().save(*args, **kwargs)

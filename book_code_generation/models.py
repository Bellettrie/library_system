import unidecode as unidecode
from django.db import models

# Create your models here.

import re
import unicodedata


def standardize_code(code: str):
    code_parts = code.split("-")
    if len(code_parts) > 2:
        try:
            code_parts[2] = str(float("0." + code_parts[2])).split(".")[1]
        except ValueError:
            pass
    return_value = code_parts[0]
    for i in range(1, len(code_parts)):
        return_value = return_value + "-" + code_parts[i]
    return return_value


class BookCode(models.Model):
    class Meta:
        abstract = True

    book_code = models.CharField(max_length=64, blank=True)
    book_code_sortable = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        self.book_code_sortable = standardize_code(self.book_code)
        super().save(*args, **kwargs)


def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """

    return unidecode.unidecode(text)


class CutterCodeRange(models.Model):
    from_affix = models.CharField(max_length=16)
    to_affix = models.CharField(max_length=16)
    number = models.CharField(max_length=16)
    generated_affix = models.CharField(max_length=20)

    @staticmethod
    def get_cutter_number(name: str):
        cutters = CutterCodeRange.objects.all().order_by("from_affix")
        result = None
        for cutter in cutters:
            if result is None:
                result = cutter
            if strip_accents(name.upper()) < cutter.from_affix:
                return result
            result = cutter
        return result


def generate_code_from_author(item):
    pub = item.publication
    auth = pub.get_authors()
    if len(auth) > 0:
        author = auth[0].creator
        code = author.identifying_code or CutterCodeRange.get_cutter_number(author.name).generated_affix
        return item.location.category.code + "-" + code + "-"
    else:
        pass


def generate_code_from_author_translated(item):
    pub = item.publication
    prefix = "N"
    if pub.is_translated:
        prefix = "V"
    auth = item.publication.get_authors()
    if len(auth) > 0:
        author = auth[0].creator.name
        return prefix + "-" + CutterCodeRange.get_cutter_number(author).generated_affix + "-"
    else:
        pass


def generate_code_abc(item):
    return item.location.category.code + "-ABC-"


def generate_code_from_title(item):
    title = item.publication.title[0:4]
    if item.location.category.code == "":
        return title + "-"
    else:
        return item.location.category.code + "-" + title + "-"


class FakeItem:
    def __init__(self, publication, location):
        self.publication = publication
        self.location = location

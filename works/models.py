from datetime import datetime

from django.db import models

# Create your models here.
from django.db.models import PROTECT, CASCADE

from book_code_generation.models import generate_code_from_author, generate_code_from_author_translated, generate_code_from_title, CutterCodeRange, BookCode
from creators.models import Creator, CreatorRole
from inventarisation.models import Inventarisation
from lendings.models import Lending


def simple_search(search_string: str):
    return Work.objects.filter(title__contains=search_string)


class NamedThing(models.Model):
    class Meta:
        abstract = True

    language = models.CharField(max_length=64, blank=True)
    article = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    sub_title = models.CharField(max_length=255, null=True, blank=True)

    def get_title(self):
        return self.article + " " + self.title if self.article else self.title


class TranslatedThing(models.Model):
    class Meta:
        abstract = True

    original_language = models.CharField(max_length=64, null=True, blank=True)
    original_article = models.CharField(max_length=64, null=True, blank=True)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    original_subtitle = models.CharField(max_length=255, null=True, blank=True)


class NamedTranslatableThing(NamedThing, TranslatedThing):
    is_translated = models.BooleanField()

    class Meta:
        abstract = True


class ItemType(models.Model):
    name = models.CharField(max_length=255)
    old_id = models.IntegerField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=8)
    item_type = models.ForeignKey(ItemType, on_delete=PROTECT)

    def __str__(self):
        return self.name


GENERATORS = {
    'author': generate_code_from_author,
    'author_translated': generate_code_from_author_translated,
    'title': generate_code_from_title,
}


class Location(models.Model):
    category = models.ForeignKey(Category, on_delete=PROTECT)
    name = models.CharField(null=True, blank=True, max_length=255)
    old_id = models.IntegerField()
    sig_gen = models.CharField(max_length=64, choices=[("Author", "author"), ("Author_Translated", "author_translated"), ("Title", "title")], default='author')

    def __str__(self):
        return self.category.name + "-" + self.name


class Work(NamedTranslatableThing):
    date_added = models.DateField()
    sorting = models.CharField(max_length=64, default='TITLE', choices=[("AUTHOR", 'Author'), ("TITLE", "Title")])
    comment = models.TextField(blank=True)
    internal_comment = models.CharField(max_length=1024, blank=True)
    old_id = models.IntegerField(blank=True, null=True)  # The ID of the same thing, in the old system.
    hidden = models.BooleanField()
    listed_author = models.CharField(max_length=64, default="ZZZZZZZZ")

    def update_listed_author(self):
        authors = self.get_authors()
        if len(authors) == 0:
            self.listed_author = "ZZZZZZ"
        else:
            self.listed_author = authors[0].creator.name + ", " + authors[0].creator.given_names + str(authors[0].creator.pk)
        self.save()

    def get_authors(self):
        from series.models import WorkInSeries

        links = CreatorToWork.objects.filter(work=self)
        authors = []
        for link in links:
            authors.append(link)
        for serie in WorkInSeries.objects.filter(work=self, is_primary=True):
            authors = serie.get_authors() + authors
        author_set = list()
        for author in authors:
            add = True
            for author_2 in author_set:
                if author.creator.name == author_2.creator.name and author.role.name == author_2.role.name:
                    add = False
            if add:
                author_set.append(author)
        author_set.sort(key=lambda a: a.number)
        return author_set

    def get_own_authors(self):
        from series.models import WorkInSeries

        links = CreatorToWork.objects.filter(work=self)
        authors = []
        for link in links:
            authors.append(link)

        author_set = list()
        for author in authors:
            add = True
            for author_2 in author_set:
                if author.creator.name == author_2.creator.name and author.role.name == author_2.role.name:
                    add = False
            if add:
                author_set.append(author)
        author_set.sort(key=lambda a: a.number)
        return author_set


class Publication(Work, BookCode):
    def is_simple_publication(self):
        return len(self.workinpublication_set) == 0

    def get_items(self):
        return Item.objects.filter(publication=self)

    def get_lend_item(self):
        for item in self.get_items():
            if len(Lending.objects.filter(item=item)) == 0:
                return item

    def get_why_no(self):
        if len(self.get_items()) == 0:
            return "Not available"
        else:
            return "Lended out"

    def get_primary_series_or_none(self):
        from series.models import Series, WorkInSeries
        series_list = WorkInSeries.objects.filter(work=self, is_primary=True)
        if len(series_list) > 0:
            return series_list[0]
        else:
            return None

    def has_no_items(self):
        return len(self.get_items()) == 0


class Item(NamedThing, BookCode):
    old_id = models.IntegerField(null=True)
    location = models.ForeignKey(Location, null=True, on_delete=PROTECT)
    publication = models.ForeignKey(Publication, on_delete=PROTECT)
    isbn10 = models.CharField(max_length=64, null=True, blank=True)
    isbn13 = models.CharField(max_length=64, null=True, blank=True)
    pages = models.CharField(null=True, blank=True, max_length=32)
    hidden = models.BooleanField()
    comment = models.TextField(default='', null=True, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    bought_date = models.DateField(default="1900-01-01", null=True, blank=True)
    added_on = models.DateField(auto_now_add=True)
    last_seen = models.DateField(null=True, blank=True)
    book_code_extension = models.CharField(max_length=16, blank=True)  # Where in the library is it?

    def get_recode(self):
        from recode.models import Recode
        recode = Recode.objects.filter(item=self)
        if len(recode) == 1:
            return recode[0]
        else:
            return None
    def display_code(self):
        return self.book_code + self.book_code_extension

    def is_available(self):
        return Lending.objects.filter(item=self, handed_in=False).count() == 0

    def current_lending(self):
        return Lending.objects.get(item=self, handed_in=False)

    def get_title(self):
        return self.title or self.publication.title

    def get_article(self):
        return self.article or self.publication.article

    def get_sub_title(self):
        return self.sub_title or self.publication.sub_title

    def get_language(self):
        return self.language or self.publication.language

    def get_original_title(self):
        return self.publication.original_title

    def get_original_sub_title(self):
        return self.publication.original_subtitle

    def get_original_article(self):
        return self.publication.original_article

    def get_original_language(self):
        return self.publication.original_language

    def get_state(self):
        states = ItemState.objects.filter(item=self).order_by("-dateTime")
        if len(states) == 0:
            return ItemState(item=self, dateTime=datetime.now(), type="AVAILABLE")
        return states[0]

    def get_prev_state(self):
        states = ItemState.objects.filter(item=self).order_by("-dateTime")
        if len(states) <= 1:
            return ItemState(item=self, dateTime=datetime.now(), type="AVAILABLE")
        return states[1]

    def is_seen(self, reason):
        state = self.get_state()
        if state.type != "AVAILABLE":
            if state.type not in not_switch_to_available:
                ItemState.objects.create(item=self, type="AVAILABLE", reason="Automatically switched because of reason: " + reason)

    def generate_code_full(self):
        first_letters = self.publication.title[0:2].lower()

        from series.models import Series, WorkInSeries
        series_list = WorkInSeries.objects.filter(work=self.publication, is_primary=True)
        if len(series_list) > 0:
            if series_list[0].number is None:
                return series_list[0].part_of_series.book_code + first_letters

            if series_list[0].number == float(int(series_list[0].number)):
                return series_list[0].part_of_series.book_code + str(int(series_list[0].number))
            else:
                return series_list[0].part_of_series.book_code + str(series_list[0].number)

        generator = GENERATORS[self.location.sig_gen]
        return generator(self) + first_letters

    def generate_code_prefix(self):
        from series.models import Series, WorkInSeries
        series_list = WorkInSeries.objects.filter(work=self.publication, is_primary=True)
        if len(series_list) > 0 and len(series_list[0].part_of_series.book_code.split("-")) > 1:
            return series_list[0].part_of_series.book_code
        generator = GENERATORS[self.location.sig_gen]
        return generator(self)

    def get_isbn10(self):
        if self.isbn10 is not None:
            return self.isbn10
        else:
            return ''

    def get_isbn13(self):
        if self.isbn13 is not None:
            return self.isbn13
        else:
            return ''

    def get_pages(self):
        if self.pages is not None:
            return self.pages
        else:
            return ''


not_switch_to_available = ["BROKEN", "SOLD"]


class ItemState(models.Model):
    item = models.ForeignKey(Item, on_delete=CASCADE)
    dateTime = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=64, choices=(("AVAILABLE", "Available"), ("MISSING", "Missing"), ("LOST", "Lost"), ("BROKEN", "Broken")))
    reason = models.TextField()
    inventarisation = models.ForeignKey(Inventarisation, null=True, blank=True, on_delete=PROTECT)


class SubWork(Work, TranslatedThing):
    def is_orphaned(self):
        return len(self.workinpublication_set) == 0

    def is_part_of_multiple(self):
        return len(self.workinpublication_set) > 1


class WorkInPublication(models.Model):
    publication = models.ForeignKey(Publication, on_delete=PROTECT)
    work = models.ForeignKey(SubWork, on_delete=PROTECT)
    number_in_publication = models.IntegerField()
    display_number_in_publication = models.CharField(max_length=64)
    unique_together = ('work', 'publication')


class CreatorToWork(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    work = models.ForeignKey(Work, on_delete=PROTECT)
    number = models.IntegerField()

    class Meta:
        unique_together = ("creator", "work", "number")

    role = models.ForeignKey(CreatorRole, on_delete=PROTECT)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.work.update_listed_author()

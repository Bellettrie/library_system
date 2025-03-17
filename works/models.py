from datetime import datetime
from django.db import models

from django.db.models import PROTECT, CASCADE, Q
from django.shortcuts import get_object_or_404

from book_code_generation.models import FakeItem, CutterCodeRange, BookCode
from book_code_generation.generators import generate_code_from_author, generate_code_from_author_translated, \
    generate_code_abc, generate_code_from_title, generate_code_abc_translated
from creators.models import Creator, CreatorRole
from inventarisation.models import Inventarisation
from lendings.models.lending import Lending
from reservations.models.reservation import Reservation
from utils.time import get_now


def simple_search(search_string: str):
    return Work.objects.filter(title__contains=search_string)


class NamedThing(models.Model):
    class Meta:
        abstract = True

    language = models.CharField(max_length=64, blank=True)
    article = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    sub_title = models.CharField(max_length=255, null=True, blank=True)
    
    search_words = models.CharField(max_length=255, null=True, blank=True)
    def get_title(self):
        return self.article + " " + self.title if self.article else self.title


class TranslatedThing(models.Model):
    class Meta:
        abstract = True

    original_language = models.CharField(max_length=64, null=True, blank=True)
    original_article = models.CharField(max_length=64, null=True, blank=True)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    original_subtitle = models.CharField(max_length=255, null=True, blank=True)

    def get_original_title(self):
        return self.original_article + " " + self.original_title if self.original_article else self.original_title


class NamedTranslatableThing(NamedThing, TranslatedThing):
    is_translated = models.BooleanField()

    def all_title_words(self, titles=None):
        full_title = ""
        if titles is None:
            titles = [ "title","sub_title", "original_title", "original_subtitle"]
        for title in titles:
            val = self.__getattribute__(title)
            if val is not None:
                full_title += " " + val
        return full_title

    class Meta:
        abstract = True


class ItemType(models.Model):
    name = models.CharField(max_length=255)
    old_id = models.IntegerField(null=True)

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
    'abc': generate_code_abc,
    'abc_translated': generate_code_abc_translated,
    'title': generate_code_from_title,
}


class Location(models.Model):
    category = models.ForeignKey(Category, on_delete=PROTECT)
    name = models.CharField(null=True, blank=True, max_length=255)
    old_id = models.IntegerField()
    sig_gen = models.CharField(max_length=64, choices=[("Author", "author"), ("Author_Translated", "author_translated"),
                                                       ("Title", "title")], default='author')

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

    def get_pub(self):
        a = Publication.objects.filter(id=self.id)
        if len(a) == 1:
            return a[0]
        return None

    def update_listed_author(self):
        authors = self.get_authors()
        if len(authors) == 0:
            self.listed_author = "ZZZZZZ"
        else:
            self.listed_author = authors[0].creator.name + ", " + authors[0].creator.given_names + str(
                authors[0].creator.pk)
        self.save()

    def get_authors(self):
        from series.models import WorkInSeries

        links = CreatorToWork.objects.filter(work_id=self.id)
        authors = []
        for link in links:
            authors.append(link)
        for serie in WorkInSeries.objects.filter(work_id=self.id, is_primary=True):
            authors = serie.get_authors() + authors
        author_set = list()
        for author in authors:
            add = True
            for author_2 in author_set:
                if author.creator.pk == author_2.creator.pk and author.role.name == author_2.role.name:
                    add = False
            if add:
                author_set.append(author)
        author_set.sort(key=lambda a: a.number)
        return author_set

    def get_own_authors(self):
        from series.models import WorkInSeries

        links = CreatorToWork.objects.filter(work_id=self.id)
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


class Publication(Work):

    def all_series(self):
        from series.models import WorkInSeries

        res = []
        for ser in WorkInSeries.objects.filter(work_id=self.id).all():
            if ser.part_of_series:
                res.append(ser.part_of_series)
                if ser.part_of_series.part_of_series:
                    res.append(ser.part_of_series.part_of_series)
                    # todo : fix this better
        return res
    def is_simple_publication(self):
        return len(self.workinpublication_set) == 0

    def get_items(self):
        return Item.objects.filter(publication_id=self.id)

    def get_lend_item(self):
        for item in self.get_items():
            if len(Lending.objects.filter(item=item)) == 0:
                return item

    def get_why_no(self):
        if len(self.get_items()) == 0:
            return "Not available"
        else:
            return "Lent out"

    def get_primary_series_or_none(self):
        from series.models import Series, WorkInSeries
        series_list = WorkInSeries.objects.filter(work_id=self.id, is_primary=True)
        if len(series_list) > 0:
            return series_list[0]
        else:
            return None

    def has_no_items(self):
        return len(self.get_items()) == 0

    def generate_code_full(self, location):
        first_letters = self.title[0:2].lower()

        from series.models import Series, WorkInSeries
        series_list = WorkInSeries.objects.filter(work_id=self.id, is_primary=True)
        if len(series_list) > 0 and series_list[0].part_of_series.book_code != "":
            if series_list[0].number is None:
                return series_list[0].part_of_series.book_code + first_letters

            if series_list[0].number == float(int(series_list[0].number)):
                return series_list[0].part_of_series.book_code + str(int(series_list[0].number))
            else:
                return series_list[0].part_of_series.book_code + str(series_list[0].number)

        generator = GENERATORS[location.sig_gen]
        val, should_not_add = generator(FakeItem(self, location))
        if should_not_add:
            return val
        else:
            return val + first_letters

    def generate_code_prefix(self, location):
        from series.models import Series, WorkInSeries
        series_list = WorkInSeries.objects.filter(work_id=self.id, is_primary=True)
        if len(series_list) > 0 and len(series_list[0].part_of_series.book_code.split("-")) > 1:
            return series_list[0].part_of_series.book_code
        generator = GENERATORS[location.sig_gen]
        return generator(FakeItem(self, location))

    def get_sub_works(self):
        return WorkInPublication.objects.filter(publication_id=self.id).order_by('number_in_publication')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from search.models import WordMatch
        WordMatch.create_all_for(self)


class Item(NamedThing, BookCode):
    old_id = models.IntegerField(null=True)
    location = models.ForeignKey(Location, on_delete=PROTECT)
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
        recode = Recode.objects.filter(item_id=self.id)
        if len(recode) == 1:
            return recode[0]
        else:
            return None

    def display_code(self):
        return self.book_code + " " + self.book_code_extension

    def in_available_state(self):
        return self.get_state().type in available_states

    def is_lent_out(self):
        return Lending.objects.filter(item_id=self.id, handed_in=False).count() > 0

    def is_available_for_lending(self):
        return self.in_available_state() and not self.is_lent_out()

    def is_reserved(self):
        reservations = Reservation.objects.filter(item_id=self.id)
        return reservations.count() > 0

    def is_available_for_reservation(self):
        return self.in_available_state() and not self.is_reserved()

    def is_reserved_for(self, member):
        reservations = Reservation.objects.filter(item_id=self.id, member=member)
        return reservations.count() > 0

    def current_lending(self):
        return get_object_or_404(Lending, item_id=self.id, handed_in=False)

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
        states = ItemState.objects.filter(item_id=self.id).order_by("-date_time")
        if len(states) == 0:
            return ItemState(item_id=self.id, date_time=get_now(), type="AVAILABLE")
        return states[0]

    def get_prev_state(self):
        states = ItemState.objects.filter(item_id=self.id).order_by("-date_time")
        if len(states) <= 1:
            return ItemState(item_id=self.id, date_time=get_now(), type="AVAILABLE")
        return states[1]

    def get_most_recent_state_not_this_inventarisation(self, inventarisation: Inventarisation):
        states = ItemState.objects.filter(item_id=self.id).exclude(inventarisation=inventarisation).order_by(
            "-date_time")
        if len(states) == 0:
            return ItemState(item_id=self.id, date_time=get_now(), type="AVAILABLE")
        return states[0]

    def is_seen(self, reason):
        state = self.get_state()
        if state.type != "AVAILABLE":
            if state.type not in not_switch_to_available:
                ItemState.objects.create(item_id=self.id, type="AVAILABLE",
                                         reason="Automatically switched because of reason: " + reason)

    def generate_code_full(self):
        return self.publication.generate_code_full(self.location)

    def generate_code_prefix(self):
        return self.publication.generate_code_prefix(self.location)

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


not_switch_to_available = ["BROKEN", "FORSALE", "SOLD", "DISPLAY", "OFFSITE", "FEATURED"]
available_states = ['AVAILABLE', 'FEATURED']


class ItemState(models.Model):
    CHOICES = (("AVAILABLE", "Available"), ("MISSING", "Missing"), ("LOST", "Lost"), ("BROKEN", "Broken"),
               ("OFFSITE", "Off-Site"), ("DISPLAY", "On Display"), ('FEATURED', "Featured"), ("SOLD", "Sold"),
               ("FORSALE", "For Sale"))
    item = models.ForeignKey(Item, on_delete=CASCADE)
    date_time = models.DateTimeField(default=datetime.now)
    type = models.CharField(max_length=64, choices=CHOICES)
    reason = models.TextField(blank=True)
    inventarisation = models.ForeignKey(Inventarisation, null=True, blank=True, on_delete=PROTECT)

    def __str__(self):
        return self.type


class SubWork(Work, TranslatedThing):
    def is_orphaned(self):
        return len(self.workinpublication_set) == 0

    def is_part_of_multiple(self):
        return len(self.workinpublication_set) > 1

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from search.models import SubWorkWordMatch
        SubWorkWordMatch.subwork_rename(self)


class WorkInPublication(models.Model):
    publication = models.ForeignKey(Publication, on_delete=PROTECT)
    work = models.ForeignKey(SubWork, on_delete=PROTECT)
    number_in_publication = models.IntegerField()
    display_number_in_publication = models.CharField(max_length=64)
    unique_together = ('work', 'publication')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from search.models import SubWorkWordMatch
        SubWorkWordMatch.subwork_rename(self.work)

    def get_authors(self):
        return self.work.get_authors()


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

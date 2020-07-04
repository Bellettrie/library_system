from datetime import datetime

from django.db import models

# Create your models here.
from django.db.models import PROTECT, CASCADE

from inventarisation.models import Inventarisation
from lendings.models import Lending


def simple_search(search_string: str):
    return Work.objects.filter(title__contains=search_string)


class NamedThing(models.Model):
    class Meta:
        abstract = True

    language = models.CharField(max_length=64)
    article = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    sub_title = models.CharField(max_length=255, null=True, blank=True)


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


class Location(models.Model):
    category = models.ForeignKey(Category, on_delete=PROTECT)
    name = models.CharField(null=True, blank=True, max_length=255)
    old_id = models.IntegerField()

    def __str__(self):
        return self.category.name + "-" + self.name


class Work(NamedTranslatableThing):
    date_added = models.DateField()
    sorting = models.CharField(max_length=64, default='TITLE', choices=[("AUTHOR", 'Author'), ("TITLE", "Title")])
    comment = models.TextField()
    internal_comment = models.CharField(max_length=1024)
    signature_fragment = models.CharField(max_length=64)
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
        for serie in WorkInSeries.objects.filter(work=self):
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


class Publication(Work):

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


class Item(NamedThing):
    old_id = models.IntegerField()
    location = models.ForeignKey(Location, null=True, on_delete=PROTECT)
    publication = models.ForeignKey(Publication, on_delete=PROTECT)
    signature = models.CharField(max_length=64)
    signature_extension = models.CharField(max_length=64)  # For getting a second copy of the same publication
    isbn10 = models.CharField(max_length=64, null=True, blank=True)
    isbn13 = models.CharField(max_length=64, null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    hidden = models.BooleanField()
    comment = models.TextField(default='')
    publication_year = models.IntegerField(null=True, blank=True)
    bought_date = models.DateField(default="1900-01-01")
    added_on = models.DateField(auto_now_add=True)
    last_seen = models.DateField(null=True, blank=True)

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


class Creator(models.Model):
    given_names = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    is_alias_of = models.ForeignKey("Creator", on_delete=PROTECT, null=True, blank=True)
    comment = models.CharField(max_length=255)
    old_id = models.IntegerField()

    def __str__(self):
        if self.is_alias_of != self:
            return self.name + "<>" + self.is_alias_of.__str__() + "::" + str(self.old_id)
        else:
            return self.name + "::" + str(self.old_id)

    def get_name(self):
        return self.given_names + ":" + self.name


class CreatorRole(models.Model):
    name = models.CharField(max_length=64, unique=True)


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


class CreatorToItem(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    item = models.ForeignKey(Item, on_delete=PROTECT)
    number = models.IntegerField()

    class Meta:
        unique_together = ("creator", "item", "number")

    role = models.ForeignKey(CreatorRole, on_delete=PROTECT)

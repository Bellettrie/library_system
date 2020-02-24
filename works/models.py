from django.db import models

# Create your models here.
from django.db.models import PROTECT

from lendings.models import Lending
from series.models import WorkInSeries


def simple_search(search_string: str):
    return Work.objects.filter(title__contains=search_string)


class Work(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    is_translated = models.BooleanField()
    original_title = models.CharField(max_length=255)
    original_subtitle = models.CharField(max_length=255)
    original_language = models.CharField(max_length=64)
    date_added = models.DateField()
    comment = models.CharField(max_length=1024)
    internal_comment = models.CharField(max_length=1024)
    signature_fragment = models.CharField(max_length=64)
    old_id = models.IntegerField(blank=True, null=True)  # The ID of the same thing, in the old system.

    def get_authors(self):
        links = CreatorToWork.objects.filter(work=self)
        authors = []
        for link in links:
            authors.append(link)
        for serie in WorkInSeries.objects.filter(work=self):
            authors = authors + serie.get_authors()
        author_set = list()
        for author in authors:
            add = True
            for author_2 in author_set:
                if author.creator.name == author_2.creator.name and author.role.name == author_2.role.name:
                    add = False
            if add:
                author_set.append(author)
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




class Item(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    old_id = models.IntegerField()
    publication = models.ForeignKey(Publication, on_delete=PROTECT)
    sticker_code = models.CharField(max_length=64)
    isbn = models.CharField(max_length=64)
    language = models.CharField(max_length=64)
    hidden = models.BooleanField()
    comment = models.CharField(max_length=1024, default='')


class SubWork(Work):
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
    name = models.CharField(max_length=255)
    is_alias_of = models.ForeignKey("Creator", on_delete=PROTECT, null=True, blank=True)
    comment = models.CharField(max_length=255)
    old_id = models.IntegerField()

    def __str__(self):
        if self.is_alias_of != self:
            return self.name + "<>" + self.is_alias_of.__str__()+ "::" + str(self.old_id)
        else:
            return self.name + "::" + str(self.old_id)


class CreatorRole(models.Model):
    name = models.CharField(max_length=64, unique=True)


class CreatorToWork(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    work = models.ForeignKey(Work, on_delete=PROTECT)
    role = models.ForeignKey(CreatorRole, on_delete=PROTECT)


class CreatorToItem(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    item = models.ForeignKey(Item, on_delete=PROTECT)
    role = models.ForeignKey(CreatorRole, on_delete=PROTECT)
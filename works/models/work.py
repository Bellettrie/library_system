from django.db import models
from django.db.models import PROTECT
from django.db.models.expressions import RawSQL

from book_code_generation.models import FakeItem
from lendings.models import Lending
from works.models.abstract import TranslatedThing, NamedTranslatableThing
from works.models.code_generators import GENERATORS


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
        from works.models.creator_to_work import CreatorToWork

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
        from works.models.creator_to_work import CreatorToWork

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
    def is_simple_publication(self):
        return len(self.workinpublication_set) == 0

    def get_items(self):
        from works.models.item import Item
        return Item.objects.annotate(available=RawSQL("SELECT coalesce(works_itemstate.type, 'AVAILABLE')= 'AVAILABLE' FROM  works_itemstate WHERE works_itemstate.item_id=works_item.id ORDER BY works_itemstate.date_time DESC LIMIT 1", [])).order_by("-available").filter(publication_id=self.id)

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
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

    # Temporary field for migration

    def as_series(self):
        from series.models import SeriesV2
        srs = SeriesV2.objects.filter(work_id=self.id)
        if len(srs) == 1:
            return srs[0]
        return None

    def part_of_series(self):
        from works.models import WorkRelation

        ws = WorkRelation.objects.filter(from_work=self, relation_kind__in=[WorkRelation.RelationKind.part_of_series])
        if len(ws) == 1:
            return ws[0]
        return None

    def get_pub(self):
        return self

    def update_listed_author(self):
        authors = self.get_authors()
        if len(authors) == 0:
            self.listed_author = "ZZZZZZ"
        else:
            self.listed_author = authors[0].creator.name + ", " + authors[0].creator.given_names + str(
                authors[0].creator.pk)
        self.save()

    def get_authors(self):
        from works.models import CreatorToWork, WorkRelation

        work_rels = WorkRelation.RelationTraversal.series_up([self.id])
        work_ids = [self.id]
        for rel in work_rels:
            work_ids.append(rel.from_work.id)
            work_ids.append(rel.to_work.id)
        work_ids = set(work_ids)

        creator_to_works = CreatorToWork.objects.filter(work_id__in=work_ids)

        result = []
        for work_id in work_ids:
            for creator in creator_to_works:
                if work_id == creator.work_id:
                    result.append(creator)
        return result

    def get_own_authors(self):
        from works.models.creator_to_work import CreatorToWork

        links = CreatorToWork.objects.filter(work_id=self.id).select_related("creator")
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

    def get_items(self):
        from works.models.item import Item
        query = """
        SELECT
            coalesce(works_itemstate.type, 'AVAILABLE')
              ='AVAILABLE'
        FROM  works_itemstate
        WHERE works_itemstate.item_id=works_item.id
        ORDER BY works_itemstate.date_time DESC
        LIMIT 1"""
        return Item.objects. \
            annotate(available=RawSQL(query, [])). \
            order_by("-available"). \
            filter(publication_id=self.id)

    def generate_code_full(self, location):
        from works.models import WorkRelation
        first_letters = self.title[0:2].lower()
        postfix = first_letters
        series_list = list(WorkRelation.RelationTraversal.series_up([self.id]))
        if ser := self.as_series():
            if ser.location_code:
                prefix = ser.location_code.gen_prefix()
                if prefix:
                    return prefix + postfix

        if len(series_list) > 0 and series_list[0].relation_index is not None:
            num = series_list[0].relation_index
            if num == float(int(num)):
                num = int(num)
            postfix = str(num)

        for rel in series_list:
            ser = rel.to_work.as_series()
            if ser and ser.book_code:
                return ser.book_code + postfix

        generator = GENERATORS[location.sig_gen]
        val, should_not_add = generator(FakeItem(self, location))
        if should_not_add:
            return val
        else:
            return val + first_letters

    def generate_code_prefix(self, location):
        from works.models import WorkRelation
        if ser := self.as_series():
            if ser.location_code:
                prefix = ser.location_code.gen_prefix()
                if prefix:
                    return prefix
        series_list = WorkRelation.RelationTraversal.series_up([self.id])

        for rel in series_list:
            ser = rel.to_work.as_series()
            if ser and ser.book_code:
                return ser.book_code

        generator = GENERATORS[location.sig_gen]
        return generator(FakeItem(self, location))

    def get_sub_works(self):
        return WorkInPublication.objects.filter(publication_id=self.id).order_by('number_in_publication')


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
    publication = models.ForeignKey(Work, on_delete=PROTECT, related_name='work_in_publication_root')
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

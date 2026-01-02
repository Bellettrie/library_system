from django.db import models
from django.db.models.expressions import RawSQL

from book_code_generation.models import FakeItem
from lendings.models import Lending
from works.models.abstract import NamedTranslatableThing
from works.models.code_generators import GENERATORS


class Work(NamedTranslatableThing):
    date_added = models.DateField()
    sorting = models.CharField(max_length=64, default='TITLE', choices=[("AUTHOR", 'Author'), ("TITLE", "Title")])
    comment = models.TextField(blank=True)
    internal_comment = models.CharField(max_length=1024, blank=True)
    old_id = models.IntegerField(blank=True, null=True)  # The ID of the same thing, in the old system.
    hidden = models.BooleanField()
    listed_author = models.CharField(max_length=64, default="ZZZZZZZZ")

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

    def __str__(self):
        return self.get_description_title()

    def get_description_title(self):
        return f"{self.get_title()} | {self.pk}"

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

    def part_of_works(self):
        from works.models import WorkRelation
        rels = WorkRelation.objects.filter(from_work_id=self.id, relation_kind=WorkRelation.RelationKind.sub_work_of)
        if len(rels) > 0:
            return rels
        return None

    def has_no_items(self):
        return len(self.get_items()) == 0

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
        from works.models import WorkRelation
        return WorkRelation.objects.filter(to_work_id=self.id,
                                           relation_kind=WorkRelation.RelationKind.sub_work_of).order_by(
            'relation_index')

    def is_deletable(self):
        from works.procedures.orphaned_work import orphaned
        return orphaned(self)

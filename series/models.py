from django.db import models

# Create your models here.
from django.db.models import PROTECT, CASCADE

from book_code_generation.models import BookCode
from creators.models import LocationNumber
from works.models import NamedTranslatableThing, Location, WorkRelation, Work, CreatorToWork


class SeriesV2(BookCode):
    work = models.OneToOneField("works.Work", on_delete=CASCADE)

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=True)
    location_code = models.ForeignKey(LocationNumber, on_delete=PROTECT, null=True, blank=True)

    def relation_index_label(self):
        wr = self.work.part_of_series()
        if wr:
            return wr.relation_index_label
        return None

    def relation_index(self):
        wr = self.work.part_of_series()
        if wr:
            return wr.relation_index
        return None

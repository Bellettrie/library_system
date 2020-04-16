from django.db import models

# Create your models here.
from django.db.models import PROTECT

from works.models import NamedTranslatableThing


class SeriesNode(models.Model):
    class Meta:
        unique_together = [['number', 'part_of_series']]
    part_of_series = models.ForeignKey("Series", on_delete=PROTECT, related_name="part", null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    display_number = models.CharField(max_length=255)
    old_id = models.IntegerField()


class Series(SeriesNode, NamedTranslatableThing):
    def get_authors(self):
        authors = []
        for author in CreatorToSeries.objects.filter(series=self):
            authors.append(author)
        if self.part_of_series is None:
            return authors
        else:
            authors += self.part_of_series.get_authors()
            return authors


class WorkInSeries(SeriesNode):
    work = models.ForeignKey("works.Work", on_delete=PROTECT)

    def get_authors(self):
        return self.part_of_series.get_authors()


class CreatorToSeries(models.Model):
    creator = models.ForeignKey("works.Creator", on_delete=PROTECT)
    series = models.ForeignKey(Series, on_delete=PROTECT)
    role = models.ForeignKey("works.CreatorRole", on_delete=PROTECT)

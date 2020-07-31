from django.db import models

# Create your models here.
from django.db.models import PROTECT

from works.models import NamedTranslatableThing


class SeriesNode(models.Model):
    class Meta:
        unique_together = [['number', 'part_of_series']]

    part_of_series = models.ForeignKey("Series", on_delete=PROTECT, related_name="part", null=True, blank=True)
    number = models.DecimalField(null=True, blank=True, decimal_places=1, max_digits=5)
    display_number = models.CharField(max_length=255)
    old_id = models.IntegerField()


class Series(SeriesNode, NamedTranslatableThing):
    book_code = models.CharField(max_length=16)  # Where in the library is it?
    def get_authors(self):
        authors = []
        for author in CreatorToSeries.objects.filter(series=self):
            authors.append(author)
        if self.part_of_series is None:
            return authors
        else:
            authors = self.part_of_series.get_authors() + authors
            return authors


class WorkInSeries(SeriesNode):
    work = models.ForeignKey("works.Work", on_delete=PROTECT)
    is_primary = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_primary and len(WorkInSeries.objects.filter(work=self.work, is_primary=True))>0:
            raise RuntimeError("Cannot Save")
        super().save(*args, **kwargs)

    def get_authors(self):
        return self.part_of_series.get_authors()


class CreatorToSeries(models.Model):
    creator = models.ForeignKey("works.Creator", on_delete=PROTECT)
    series = models.ForeignKey(Series, on_delete=PROTECT)
    number = models.IntegerField()

    class Meta:
        unique_together = ("creator", "series", "number")

    role = models.ForeignKey("works.CreatorRole", on_delete=PROTECT)

from tkinter import CASCADE

from django.db import models

# Create your models here.
from django.db.models import PROTECT

from works.models import SubWork, Work, Creator, CreatorRole


class SeriesNode(models.Model):
    part_of_series = models.ForeignKey("SeriesNode", on_delete=PROTECT, related_name="part", null=True,blank=True)
    number = models.IntegerField()
    display_number = models.CharField(max_length=255)
    old_id = models.IntegerField()


class Series(SeriesNode):
    pass


class WorkInSeries(SeriesNode):
    work = models.ForeignKey(Work, on_delete=PROTECT)


class CreatorToSeries(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    series = models.ForeignKey(Series, on_delete=PROTECT)
    role = models.ForeignKey(CreatorRole, on_delete=PROTECT)
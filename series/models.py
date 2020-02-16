from tkinter import CASCADE

from django.db import models

# Create your models here.
from django.db.models import PROTECT

from works.models import SubWork


class Series(models.Model):
    name = models.CharField(max_length=255)

    def check_consistency(self):
        # combine turtle and hare with
        found = set()
        first = True
        for i in SubWork.objects.filter(series=self):
            pass


class WorkNode(models.Model):
    work = models.ForeignKey(SubWork, null=True, blank=True, on_delete=CASCADE)
    series = models.ForeignKey(Series, on_delete=PROTECT, related_name='part')

    def root_detect(self):
        pass


class WorkIsPartOfWork(models.Model):
    connected_to = models.ForeignKey(WorkNode, on_delete=PROTECT, related_name='item')
    work_node = models.ForeignKey(WorkNode, on_delete=CASCADE)
    series = models.ForeignKey(Series, on_delete=PROTECT, related_name='part')

    sort_number = models.IntegerField(unique=True)
    display_number = models.CharField(max_length=128)


from django.db import models

# Create your models here.
from django.db.models import PROTECT


class Publication(models.Model):
    name = models.CharField(max_length=255)


class Item(models.Model):
    name = models.CharField(max_length=255)
    publication = models.ForeignKey(Publication, on_delete=PROTECT)


class WorkInItem(models.Model):
    item = models.ForeignKey(Item, on_delete=PROTECT)
    work = models.ForeignKey("Work", on_delete=PROTECT)
    count = models.IntegerField()


class Work(models.Model):
    name = models.CharField(max_length=255)


class Creator(models.Model):
    name = models.CharField(max_length=255)


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)


class AuthorToWork(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    work = models.ForeignKey(Work, on_delete=PROTECT)
    role = models.ForeignKey(Role, on_delete=PROTECT)


class AuthorToPublication(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    work = models.ForeignKey(Work, on_delete=PROTECT)
    role = models.ForeignKey(Role, on_delete=PROTECT)
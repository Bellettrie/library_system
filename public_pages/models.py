from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Committee


class PublicPageGroup(models.Model):
    name = models.CharField(max_length=64)
    committees = models.ForeignKey(Committee, on_delete=PROTECT)


class PublicPage(models.Model):
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    text = models.TextField()
    group = models.ForeignKey(PublicPageGroup, on_delete=PROTECT)

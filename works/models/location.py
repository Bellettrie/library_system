from django.db import models
from django.db.models import PROTECT

from works.models.category import Category


class Location(models.Model):
    category = models.ForeignKey(Category, on_delete=PROTECT)
    name = models.CharField(null=True, blank=True, max_length=255)
    old_id = models.IntegerField()
    sig_gen = models.CharField(max_length=64, choices=[("Author", "author"), ("Author_Translated", "author_translated"),
                                                       ("Title", "title")], default='author')

    def __str__(self):
        return self.category.name + "-" + self.name

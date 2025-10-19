from django.db import models
from django.db.models import PROTECT


class ItemType(models.Model):
    name = models.CharField(max_length=255)
    old_id = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=8)
    item_type = models.ForeignKey(ItemType, on_delete=PROTECT)

    def __str__(self):
        return self.name
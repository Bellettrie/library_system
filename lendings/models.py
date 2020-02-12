from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Member
from works.models import Item


class Lending(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey(Item, on_delete=PROTECT)

from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Member
from works.models import Item


class Lending(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey(Item, on_delete=PROTECT)

    lended_on = models.DateField()
    lended_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="lended_out")
    times_extended = models.IntegerField(default=0)
    last_extended = models.DateField()
    end_date = models.DateField()
    handed_in = models.BooleanField()
    handed_in_on = models.DateField()
    handed_in_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="handed_in")
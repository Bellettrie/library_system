from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Member


class Lending(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey("works.Item", on_delete=PROTECT)
    lended_on = models.DateField()
    lended_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="lended_out", null=True, blank=True)
    times_extended = models.IntegerField(default=0)
    last_extended = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    handed_in = models.BooleanField()
    handed_in_on = models.DateField(null=True, blank=True)
    handed_in_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="handed_in", null=True, blank=True)


class Reservation(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey("works.Item", on_delete=PROTECT)
    reserved_on = models.DateField()
    reserved_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="reservatin_action_by")
    reservation_end_date = models.DateField(null=True, blank=True)

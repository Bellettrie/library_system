import math
from datetime import datetime

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

    def is_extendable(self, getfine):
        return (datetime.now().date() <= self.end_date) | getfine

    def is_late(self):
        return datetime.now() > self.end_date

    def calculate_fine(self):
        from config.models import LendingSettings

        if self.end_date > datetime.date(datetime.now()):
            return 0
        fine_per_week, max_fine = LendingSettings.get_fine_settings(self.item, self.member)
        return format(min((math.ceil((datetime.date(datetime.now()) - self.end_date).days / 7)*fine_per_week), max_fine)/100, '.2f')


class Reservation(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey("works.Item", on_delete=PROTECT)
    reserved_on = models.DateField()
    reserved_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="reservation_action_by")
    reservation_end_date = models.DateField(null=True, blank=True)

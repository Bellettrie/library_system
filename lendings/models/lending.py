from datetime import datetime, timedelta

from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models.member import Member
from datetime import date

from utils.time import get_today


class Lending(models.Model):
    class Meta:
        permissions = [('extend', 'Can extend lending'),
                       ('extend_with_fine', 'Extend book even though it has a fine'),
                       ('return', 'Return book')]

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
    start_date = models.DateField(default=date.today)
    last_mailed = models.DateTimeField(default="1900-01-01")

    # This flag will be used to differentiate between having mailed for being almost too late, and having mailed for being late.
    mailed_for_late = models.BooleanField(default=False)

    def is_simple_extendable(self, now=None):
        if now is None:
            now = get_today()

        return not self.handed_in and now <= self.end_date

    def is_extendable(self, get_fine, now=None):
        return self.is_simple_extendable(now) | get_fine

    def is_at_extend_limit(self):
        from config.models import LendingSettings
        return self.times_extended < LendingSettings.get_for(self.item, self.member).extend_count

    def is_late(self, now=None):
        if now is None:
            now = get_today()
        return now > self.end_date

    def is_almost_late(self, now=None):
        if now is None:
            now = get_today()
        return self.end_date - timedelta(days=4) < now

    def calculate_fine(self):
        from lendings.procedures.get_total_fine import get_total_fine_for_lending
        return format(get_total_fine_for_lending(self, get_today()) / 100, '.2f')

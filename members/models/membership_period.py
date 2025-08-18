from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT

from members.models.member_background import MemberBackground
from members.models.membership_type import MembershipType


class MembershipPeriod(models.Model):
    member = models.ForeignKey("Member", on_delete=PROTECT, null=True)
    start_date = models.DateField(null=True, blank=False)
    end_date = models.DateField(null=True, blank=True)
    member_background = models.ForeignKey(MemberBackground, on_delete=PROTECT, null=True)
    membership_type = models.ForeignKey(MembershipType, on_delete=PROTECT, null=True)

    def clean(self):
        if self.end_date is not None and self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'Start Date is greater than End Date'})

from datetime import datetime, timedelta

from django.db import models

# Create your models here.
from django.db.models import PROTECT
from django.utils import timezone

from mail.models import mail_member
from members.models import Member
from datetime import date


class Reservation(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey("works.Item", on_delete=PROTECT)
    reserved_on = models.DateField()
    reserved_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="reservation_action_by")
    reservation_end_date = models.DateField(null=True, blank=True)

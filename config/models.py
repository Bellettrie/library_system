from datetime import datetime, timedelta

from django.contrib.admin import register
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.
from django.db.models import PROTECT
from django.urls import reverse

from members.models import Member
from works.models import ItemType, Item


class Holiday(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    starting_date = models.DateField()
    ending_date = models.DateField()
    skipped_for_fine = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('holiday.view', kwargs={'pk': self.pk})


class LendingSettings(models.Model):
    item_type = models.ForeignKey(ItemType, on_delete=PROTECT)
    term_for_inactive = models.IntegerField()
    term_for_active = models.IntegerField()
    hand_in_days = models.IntegerField(default=1)
    borrow_money_inactive = models.IntegerField()  # in cents
    borrow_money_active = models.IntegerField()  # in cents
    fine_amount = models.IntegerField()  # in cents
    max_fine = models.IntegerField()  # in cents

    @staticmethod
    def get_term(item: Item, member: Member):
        try:
            # try something
            ls = LendingSettings.objects.get(item_type=item.publication.location.category.item_type)
            if member.is_active():
                return ls.term_for_active
            else:
                return ls.term_for_inactive
        except ObjectDoesNotExist:
            print("Term not found")
            return 7

    @staticmethod
    def get_handin_days(item: Item, member: Member):
        try:
            # try something
            ls = LendingSettings.objects.get(item_type=item.publication.location.category.item_type)
            return ls.hand_in_days
        except ObjectDoesNotExist:
            print("Term not found")
            return 1

    @staticmethod
    def get_end_date(item: Item, member: Member, start_date=None):
        if start_date is None:
            start_date = datetime.date(datetime.now)
        term = LendingSettings.get_term(item, member)
        hand_in_days = LendingSettings.get_handin_days(item, member)
        holidays = Holiday.objects.filter(ending_date__gte=start_date).order_by('-starting_date')

        total_days = 0
        while term > 0:
            total_days = total_days + 1
            is_holiday_day = False
            now_date = start_date + timedelta(days=total_days)
            if len(holidays) > 0:
                while holidays[0].ending_date < now_date:
                    holidays = holidays[1:]
                    if len(holidays) == 0:
                        break
            if len(holidays) > 0 and holidays[0].starting_date > start_date + timedelta(days=term):
                is_holiday_day = True
            if not (term <= hand_in_days and is_holiday_day):
                term = term - 1

        return start_date + timedelta(days=total_days)

    @staticmethod
    def get_fine_settings(item, member):
        try:
            # try something
            ls = LendingSettings.objects.get(item_type=item.publication.location.category.item_type)
            return ls.fine_amount, ls.max_fine
        except ObjectDoesNotExist:
            print("Term not found")
            return 10000, 1000000

    def __str__(self):
        return self.item_type.name

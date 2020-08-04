import math
from datetime import datetime, timedelta

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

    def save(self, *args, **kwargs):
        from lendings.models import Lending
        super().save(*args, **kwargs)
        lendings = Lending.objects.filter(end_date__gt=self.starting_date, handed_in=False)
        print("A")
        print(len(lendings))
        for lending in lendings:
            if lending.is_late():
                print("LATE")

                continue
            new_end = lending.calc_end_date(lending.member, lending.item, lending.start_date)

            print(new_end)
            if lending.end_date < new_end:

                lending.end_date = new_end
                lending.save()


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
            ls = LendingSettings.objects.get(item_type=item.location.category.item_type)
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
            ls = LendingSettings.objects.get(item_type=item.location.category.item_type)
            return ls.hand_in_days
        except ObjectDoesNotExist:
            print("Term not found")
            return 1

    @staticmethod
    def get_end_date(item: Item, member: Member, start_date=None):
        if start_date is None:
            start_date = datetime.date(datetime.now())
        term = LendingSettings.get_term(item, member)
        hand_in_days = LendingSettings.get_handin_days(item, member)
        holidays = Holiday.objects.filter(ending_date__gte=start_date).order_by('starting_date')

        total_days = 0
        while term > 0:
            total_days = total_days + 1
            now_date = start_date + timedelta(days=total_days)
            is_holiday_day, holidays = LendingSettings.handle_holiday_day(holidays, now_date)

            if not (term <= hand_in_days and is_holiday_day):
                term = term - 1
        end_date = start_date + timedelta(days=total_days)
        if member.end_date is None:
            return end_date
        else:
            return min(end_date, member.end_date)

    @staticmethod
    def handle_holiday_day(holiday_list, current_date):
        if len(holiday_list) > 0:
            while holiday_list[0].ending_date < current_date:
                holiday_list = holiday_list[1:]
                if len(holiday_list) == 0:
                    break
        return len(holiday_list) > 0 and holiday_list[0].starting_date <= current_date, holiday_list

    @staticmethod
    def get_borrow_money(ls, member):
        if member.is_active():
            return ls.borrow_money_active
        else:
            return ls.borrow_money_inactive

    @staticmethod
    def get_fine_settings(item, member):
        try:
            # try something
            ls = LendingSettings.objects.get(item_type=item.location.category.item_type)
            return ls.fine_amount + LendingSettings.get_borrow_money(ls, member), ls.max_fine
        except ObjectDoesNotExist:
            print("Term not found")
            return 10000, 1000000

    def __str__(self):
        return self.item_type.name

    @staticmethod
    def get_fine_days(ending_date: datetime.date, current_date=None):
        if current_date is None:
            current_date = datetime.date(datetime.now())
        holidays = Holiday.objects.filter(ending_date__gte=ending_date, skipped_for_fine=False).order_by('starting_date')
        counted_date = ending_date
        days = 0
        while counted_date < current_date:
            counted_date = counted_date + timedelta(days=1)
            is_holiday_day, holidays = LendingSettings.handle_holiday_day(holidays, counted_date)

            if not is_holiday_day:
                days = days + 1
        return days

    @staticmethod
    def get_fine(item: Item, member: Member, ending_date: datetime.date, current_date=None):
        days = LendingSettings.get_fine_days(ending_date, current_date)
        fine_per_week, max_fine = LendingSettings.get_fine_settings(item, member)
        weeks = math.ceil(days / 7)
        return min(max_fine, fine_per_week * weeks)

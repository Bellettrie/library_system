import math
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.
from django.db.models import PROTECT
from django.urls import reverse

from members.models import Member

WEEKEND_DAYS = [5, 6]


class Holiday(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    starting_date = models.DateField()
    ending_date = models.DateField()
    skipped_for_fine = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('holiday.view', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        from lendings.procedures.get_end_date import get_end_date_for_lending
        from lendings.models import Lending

        super().save(*args, **kwargs)
        lendings = Lending.objects.filter(end_date__gt=self.starting_date, handed_in=False)

        for lending in lendings:
            # Late lendings do not get recalculated?
            if lending.is_late():
                continue

            # Import here to prevent circular import
            new_end = get_end_date_for_lending(lending, lending.start_date)

            if lending.end_date < new_end:
                lending.end_date = new_end
                lending.save()

    # This function finds the first available day before given day, that is not in a holiday or weekend.
    @staticmethod
    def get_handin_day_before_or_on(handin_date: datetime.date):
        should_continue = True
        holidays = list(Holiday.objects.all())

        while should_continue:
            should_continue = False
            for holiday in holidays:
                if holiday.starting_date <= handin_date <= holiday.ending_date or handin_date.weekday() in WEEKEND_DAYS:
                    should_continue = True
            if should_continue:
                handin_date -= timedelta(days=1)
        return handin_date

    # This function finds the first available day after given day, that is not in a holiday or weekend.
    @staticmethod
    def get_handin_day_after_or_on(handin_date: datetime.date):
        should_continue = True
        holidays = list(Holiday.objects.all())

        while should_continue:
            should_continue = False
            for holiday in holidays:
                if holiday.starting_date <= handin_date <= holiday.ending_date or handin_date.weekday() in WEEKEND_DAYS:
                    should_continue = True
            if should_continue:
                handin_date += timedelta(days=1)
        return handin_date


class LendingSettings(models.Model):
    item_type = models.ForeignKey("works.ItemType", on_delete=PROTECT)
    member_is_active = models.BooleanField(default=False)

    term = models.IntegerField()
    borrow_money = models.IntegerField()  # in cents
    fine_amount = models.IntegerField()  # in cents, per week
    max_fine = models.IntegerField()  # in cents
    max_count = models.IntegerField()  # how often can you extend the book?

    extend_count = models.IntegerField()

    def __str__(self):
        return "{}: {}".format(self.item_type.name, "active" if self.member_is_active else "inactive")

    @staticmethod
    def get_for_type(item_type, member_is_active: bool):
        if member_is_active:
            try:
                return LendingSettings.objects.get(item_type=item_type, member_is_active=True)
            except LendingSettings.DoesNotExist:
                pass
            print("No special case for active member for item type {}".format(item_type))

        # Mind the fall-through; this statement happens either if the member isn't active,
        #   or if no settings exist for the active member specifically.
        return LendingSettings.objects.get(item_type=item_type, member_is_active=False)

    @staticmethod
    def get_for(item, member: Member):
        return LendingSettings.get_for_type(item.location.category.item_type, member.is_active())

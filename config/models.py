import math
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.
from django.db.models import PROTECT
from django.urls import reverse

from members.models import Member


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

        for lending in lendings:
            # Late lendings do not get recalculated?
            if lending.is_late():
                continue

            # Import here to prevent circular import
            from lendings.procedures.get_end_date import get_end_date_for_lending
            new_end = get_end_date_for_lending(lending, lending.start_date)

            if lending.end_date < new_end:
                lending.end_date = new_end
                lending.save()

    # This function finds the first available day that is not in holiday.
    @staticmethod
    def get_handin_day_after_or_on(handin_date: datetime.date):
        should_continue = True
        holidays = list(Holiday.objects.all())

        while should_continue:
            should_continue = False
            for holiday in holidays:
                if holiday.starting_date <= handin_date <= holiday.ending_date:
                    should_continue = True
            if should_continue:
                handin_date += timedelta(days=1)
        return handin_date

    @staticmethod
    def get_handin_day_before_or_on(handin_date: datetime.date):
        should_continue = True
        holidays = list(Holiday.objects.all())

        while should_continue:
            should_continue = False
            for holiday in holidays:
                if holiday.starting_date <= handin_date <= holiday.ending_date:
                    should_continue = True
            if should_continue:
                handin_date -= timedelta(days=1)
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

    @staticmethod
    def get_for(item, member: Member):
        if member.is_active():
            try:
                print("B")
                return LendingSettings.objects.get(item_type=item.location.category.item_type, member_is_active=True)
            except LendingSettings.DoesNotExist:
                print("HERE")
                pass
            print("No special case for active member for item type {}".format(item.location.category.item_type))

        return LendingSettings.objects.get(item_type=item.location.category.item_type, member_is_active=False)

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

    def get_absolute_url(self):
        return reverse('holiday.view', kwargs={'pk': self.pk})


class LendingSettings(models.Model):
    item_type = models.ForeignKey(ItemType, on_delete=PROTECT)
    term_for_inactive = models.IntegerField()
    term_for_active = models.IntegerField()
    borrow_money_inactive = models.IntegerField()     # in cents
    borrow_money_active = models.IntegerField()     # in cents

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

    def __str__(self):
        return self.item_type.name
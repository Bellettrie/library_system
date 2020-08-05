from django.db import models

# Create your models here.
from django.db.models import PROTECT

from book_code_generation.models import CutterCodeRange


class Creator(models.Model):
    given_names = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    is_alias_of = models.ForeignKey("Creator", on_delete=PROTECT, null=True, blank=True)
    comment = models.CharField(max_length=255)
    old_id = models.IntegerField()

    def __str__(self):
        if self.is_alias_of != self:
            return self.name + "<>" + self.is_alias_of.__str__() + "::" + str(self.old_id)
        else:
            return self.name + "::" + str(self.old_id)

    def get_name(self):
        return self.given_names + ":" + self.name

    identifying_code = models.CharField(null=True, max_length=16)

    def fill_identifying_code(self):
        self.identifying_code = CutterCodeRange.get_cutter_number(self.name).generated_affix
        self.save()


class CreatorRole(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

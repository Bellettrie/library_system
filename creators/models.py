from django.db import models

# Create your models here.
from django.db.models import PROTECT, CASCADE



class Creator(models.Model):
    given_names = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    is_alias_of = models.ForeignKey("Creator", on_delete=PROTECT, null=True, blank=True)
    comment = models.CharField(max_length=255)
    old_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.is_alias_of != self:
            return self.name + "<>" + self.is_alias_of.__str__() + "::" + str(self.old_id)
        else:
            return self.name + "::" + str(self.old_id)

    def get_name(self):
        return self.given_names + " " + self.name

    def get_canonical_name(self):
        return self.given_names + " " + self.name + "   (" + str(self.pk) + ")"


class CreatorRole(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class CreatorLocationNumber(models.Model):
    creator = models.ForeignKey(Creator, on_delete=CASCADE)
    location = models.ForeignKey('works.location', on_delete=CASCADE)
    number = models.IntegerField()
    letter = models.CharField(max_length=16)
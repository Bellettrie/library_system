from django.db import models

# Create your models here.
from django.db.models import PROTECT, CASCADE


class Creator(models.Model):
    given_names = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    is_alias_of = models.ForeignKey("Creator", on_delete=PROTECT, null=True, blank=True)
    comment = models.CharField(max_length=255)
    old_id = models.IntegerField(null=True, blank=True)
    mark_for_change = models.BooleanField(default=False)

    def __str__(self):
        if self.is_alias_of != self:
            return self.name + "<>" + self.is_alias_of.__str__() + "::" + str(self.old_id)
        else:
            return self.name + "::" + str(self.old_id)

    def get_name(self):
        return self.given_names + " " + self.name

    def get_canonical_name(self):
        return self.given_names + " " + self.name + "   (" + str(self.pk) + ")"

    def get_all_items(self):
        result = []
        from works.models import Item, Publication
        for work in Publication.objects.filter(creatortowork__creator=self):
            for item in Item.objects.filter(publication=work):
                result.append(item)
        return result


class CreatorRole(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class CreatorLocationNumber(models.Model):
    creator = models.ForeignKey(Creator, on_delete=CASCADE)
    location = models.ForeignKey('works.Location', on_delete=CASCADE)
    number = models.IntegerField()
    letter = models.CharField(max_length=16)


def force_relabel(creatorlocationnumber: CreatorLocationNumber, old_number: int, old_letter: str):
    from recode.models import Recode

    items = creatorlocationnumber.creator.get_all_items()
    location_code = creatorlocationnumber.location.category.code
    for item in items:
        if item.location != creatorlocationnumber.location:
            items.remove(item)

    for item in items:
        recodes = Recode.objects.filter(item=item)
        if len(recodes) > 0:
            recode = recodes[0]
            if recode.book_code_sortable.startswith(location_code + "-" + old_letter + "-" + str(old_number)):
                print("Change recode")
        else:
            if item.book_code_sortable.startswith(location_code + "-" + old_letter + "-" + str(old_number)):
                print("Change Item")

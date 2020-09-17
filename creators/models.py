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

    def get_all_series(self):
        result = []
        from series.models import Series
        for work in Series.objects.filter(creatortoseries__creator=self):
            result.append(work)
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


def try_to_update_object(my_object, pattern, new_prefix):
    match = pattern.match(my_object.book_code)
    if match:
        my_object.book_code = new_prefix + my_object.book_code[match.end():]
        print(my_object.book_code)
        my_object.save()
def update_item(item, creatortonumber, pattern, old_prefix, new_prefix):
    from recode.models import Recode

    recodes = Recode.objects.filter(item=item)
    if len(recodes) > 0:
        recode = recodes[0]
        try_to_update_object(recode, pattern, new_prefix)
    else:
        match = pattern.match(item.book_code)
        if match:
            new_code = new_prefix + item.book_code[match.end():]
            Recode.objects.create(item=item, book_code=new_code, book_code_extension=item.book_code_extension)


def force_relabel(creatorlocationnumber: CreatorLocationNumber, old_number: int, old_letter: str):
    from series.models import WorkInSeries
    from works.models import Publication, Item
    items = creatorlocationnumber.creator.get_all_items()
    location_code = creatorlocationnumber.location.category.code
    for item in items:
        if item.location != creatorlocationnumber.location :
            print("DEAD")

        if item.publication.get_authors()[
            0].creator != creatorlocationnumber.creator:
            items.remove(item)
            print("undead")
    import re

    old_prefix = location_code + "-" + old_letter + "-" + str(old_number)
    new_prefix = location_code + "-" + creatorlocationnumber.letter + "-" + str(creatorlocationnumber.number) + "-"
    pattern = re.compile("^" + location_code + "-" + old_letter + "-" + str(old_number) + "0*-")

    for item in items:
        update_item(item, creatorlocationnumber, pattern, old_prefix, new_prefix)

    all_series = creatorlocationnumber.creator.get_all_series()

    series_handle_list = []
    for series in all_series:
        if series.location == creatorlocationnumber.location:
            if pattern.match(series.book_code_sortable):
                try_to_update_object(series, pattern, new_prefix)
                series_handle_list.append(series)

    to_handle = True
    while to_handle:
        to_handle = False
        new_series_list = []
        for series in series_handle_list:
            to_handle = True
            for work_in_series in WorkInSeries.objects.filter(part_of_series=series, is_primary=True):
                items = Item.objects.filter(publication__workinseries=work_in_series)
                for item in items:
                    update_item(item, creatorlocationnumber, pattern, old_prefix, new_prefix)
            if series.part_of_series:
                new_series_list.append(series.part_of_series)
        series_handle_list = new_series_list

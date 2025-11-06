import re

from django.db import models

# Create your models here.
from django.db.models import PROTECT, CASCADE


class LocationNumber(models.Model):
    location = models.ForeignKey('works.Location', on_delete=CASCADE, null=True, blank=True)
    number = models.IntegerField()
    letter = models.CharField(max_length=16)
    name = models.CharField(max_length=64, null=True, blank=True)
    auto_name = models.BooleanField(default=True)


class Creator(models.Model):
    given_names = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    is_alias_of = models.ForeignKey("Creator", on_delete=PROTECT, null=True, blank=True)
    comment = models.CharField(max_length=255)
    old_id = models.IntegerField(null=True, blank=True)
    mark_for_change = models.BooleanField(default=False)

    def __str__(self):
        if self.is_alias_of != self:
            return self.name + "<>" + self.is_alias_of.__str__() + "::" + str(self.old_id) + "--" + str(self.pk)
        else:
            return self.name + "::" + str(self.old_id) + "--" + str(self.pk)

    def get_name(self):
        return self.given_names + " " + self.name

    def get_canonical_name(self):
        return self.name + ", " + self.given_names + "   (" + str(self.pk) + ")"

    def get_all_items(self):
        result = []
        from works.models import Item, Work
        creators = set(Creator.objects.filter(is_alias_of_id=self.id))
        creators.add(self)
        if self.is_alias_of:
            creators.add(self.is_alias_of)
        for work in Work.objects.filter(creatortowork__creator__in=creators):
            for item in Item.objects.filter(publication=work):
                result.append(item)
        return result

    def get_all_publications(self):
        result = []
        from works.models import Item, Work
        creators = set(Creator.objects.filter(is_alias_of_id=self.id))
        creators.add(self)
        if self.is_alias_of:
            creators.add(self.is_alias_of)
        for work in Work.objects.filter(creatortowork__creator__in=creators):
            result.append(work)
        for creator in creators:
            for s in creator.get_all_series():
                s.part_of_series_update()
        return result

    def author_word_search_update(self):
        from search.models import AuthorWordMatch
        AuthorWordMatch.author_rename(self)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.author_word_search_update()

    def get_all_series(self):

        from series.models import Series
        result = set(Series.objects.filter(creatortoseries__creator_id=self.id))
        result_len = 0
        while result_len < len(result):
            result_len = len(result)
            result = result | set(Series.objects.filter(part_of_series__in=result))
        return result

    def get_location_item_counts(self, location, author_item_dict):

        from recode.models import Recode
        from works.models import Item

        new_recode = 0
        old_recode = 0
        non_automa = 0
        code = None
        try:
            code = CreatorLocationNumber.objects.get(creator_id=self.id, location_id=location.id)
        except CreatorLocationNumber.DoesNotExist:
            pass
        for item in author_item_dict.get(self, []):
            if len(Recode.objects.filter(item=item)) > 0:
                old_recode += 1
            else:
                if not code or re.match("^" + location.category.code + "-" + code.letter + "-" + str(code.number) + "0*-", item.book_code):
                    new_recode += 1
                else:
                    non_automa += 1
        return (new_recode, old_recode, non_automa)


class CreatorRole(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class CreatorLocationNumber(LocationNumber):
    # pass
    creator = models.ForeignKey(Creator, on_delete=CASCADE)

    def save(self, *args, **kwargs):
        self.name = self.creator.get_canonical_name()
        self.auto_name = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.letter + "-" + str(self.number) + ":" + str(self.location.pk) + ":" + str(self.creator.pk)

    def get_name(self):
        if self.name:
            return self.name


def try_to_update_object(my_object, pattern, new_prefix):
    match = pattern.match(my_object.book_code)
    if match:
        my_object.book_code = new_prefix + my_object.book_code[match.end():]
        my_object.save()


def update_item(item, pattern, old_prefix, new_prefix):
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


def relabel_creator(creator, location, old_number, old_letter, new_number, new_letter):
    creators = Creator.objects.filter(is_alias_of=creator)

    for creatorn in creators:
        if creatorn != creator:
            relabel_creator(creatorn, location, old_number, old_letter, new_number, new_letter)
    from series.models import WorkInSeries
    from works.models import Item
    items = creator.get_all_items()
    location_code = location.category.code
    for item in items:
        if item.location != location:
            items.remove(item)
        if item.publication.get_authors()[0].creator != creator:
            if item in items:
                items.remove(item)
    import re

    old_prefix = location_code + "-" + old_letter + "-" + str(old_number)
    new_prefix = location_code + "-" + new_letter + "-" + str(new_number) + "-"
    pattern = re.compile("^" + location_code + "-" + old_letter + "-" + str(old_number) + "0*-")

    for item in items:
        update_item(item, pattern, old_prefix, new_prefix)

    all_series = creator.get_all_series()

    series_handle_list = []
    for series in all_series:
        if series.location == location:
            if pattern.match(series.book_code_sortable):
                try_to_update_object(series, pattern, new_prefix)
                series_handle_list.append(series)
        else:
            print(series.location, location)

    to_handle = True
    while to_handle:
        to_handle = False
        new_series_list = []
        for series in series_handle_list:
            to_handle = True
            for work_in_series in WorkInSeries.objects.filter(part_of_series=series, is_primary=True):
                items = Item.objects.filter(publication__workinseries=work_in_series)
                for item in items:
                    update_item(item, pattern, old_prefix, new_prefix)
            if series.part_of_series:
                new_series_list.append(series.part_of_series)
        series_handle_list = new_series_list


def force_relabel(creatorlocationnumber: CreatorLocationNumber, old_number: int, old_letter: str):
    relabel_creator(creatorlocationnumber.creator, creatorlocationnumber.location, old_number, old_letter, creatorlocationnumber.number, creatorlocationnumber.letter)

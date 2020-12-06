from django.db import models

# Create your models here.
from django.db.models import PROTECT

from book_code_generation.models import BookCode, FakeItem
from creators.models import LocationNumber
from works.models import NamedTranslatableThing, Location, GENERATORS


class SeriesNode(models.Model):
    class Meta:
        unique_together = [['number', 'part_of_series']]

    part_of_series = models.ForeignKey("Series", on_delete=PROTECT, related_name="part", null=True, blank=True)
    number = models.DecimalField(null=True, blank=True, decimal_places=1, max_digits=5)
    display_number = models.CharField(max_length=255, blank=True)
    old_id = models.IntegerField(null=True, blank=True)

    def things_underneath(self):
        return SeriesNode.objects.filter(part_of_series=self).order_by('number')

    def is_series(self):
        try:
            return Series.objects.get(pk=self.pk)
        except Series.DoesNotExist:
            return None

    def is_work(self):
        try:
            return WorkInSeries.objects.get(pk=self.pk)
        except WorkInSeries.DoesNotExist:
            return None


class Series(SeriesNode, NamedTranslatableThing, BookCode):
    book_code = models.CharField(max_length=16)  # Where in the library is it?
    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=True)
    location_code = models.ForeignKey(LocationNumber, on_delete=PROTECT, null=True, blank=True)

    def get_authors(self):
        authors = []
        for author in CreatorToSeries.objects.filter(series=self):
            authors.append(author)
        if self.part_of_series is None:
            return authors
        else:
            authors = self.part_of_series.get_authors() + authors
            return authors

    def get_own_authors(self):
        authors = []
        for author in CreatorToSeries.objects.filter(series=self):
            authors.append(author)
        return authors

    def get_canonical_title(self):
        str = ""
        if self.part_of_series:
            str = self.part_of_series.get_canonical_title() + " > "
        return str + self.title

    def generate_code_full(self, location):
        first_letters = self.title[0:2].lower()

        if self.part_of_series and self.part_of_series.book_code:
            pos = self.part_of_series.book_code
            if self.number is None:
                return pos + first_letters

            if self.number == float(int(self.number)):
                return pos + str(int(self.number))
            else:
                return pos + str(self.number)

        generator = GENERATORS[location.sig_gen]
        val, should_not_add = generator(FakeItem(self, location))
        if should_not_add:
            return val
        else:
            return val + first_letters

    def generate_code_prefix(self, location):
        if self.part_of_series and self.part_of_series.book_code:
            return self.part_of_series.book_code
        generator = GENERATORS[location.sig_gen]
        return generator(FakeItem(self, location))

    def get_all_items(self):
        pass


class WorkInSeries(SeriesNode):
    work = models.ForeignKey("works.Work", on_delete=PROTECT)
    is_primary = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_primary and len(WorkInSeries.objects.filter(work=self.work, is_primary=True)) > 0:
            raise RuntimeError("Cannot Save")
        super().save(*args, **kwargs)

    def get_authors(self):
        return self.part_of_series.get_authors()


class CreatorToSeries(models.Model):
    creator = models.ForeignKey("creators.Creator", on_delete=PROTECT)
    series = models.ForeignKey(Series, on_delete=PROTECT)
    number = models.IntegerField(blank=True)

    class Meta:
        unique_together = ("creator", "series", "number")

    role = models.ForeignKey("creators.CreatorRole", on_delete=PROTECT)

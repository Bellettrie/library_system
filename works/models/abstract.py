from django.db import models


class NamedThing(models.Model):
    class Meta:
        abstract = True

    language = models.CharField(max_length=64, blank=True)
    article = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    sub_title = models.CharField(max_length=255, null=True, blank=True)

    def get_title(self):
        if not self.title:
            return ""
        if self.article:
            return self.article + " " + self.title
        return self.title

    def get_title_or_no_title(self):
        title= self.get_title()
        if title != "":
            return title
        return "<No Title>"

class TranslatedThing(models.Model):
    class Meta:
        abstract = True

    original_language = models.CharField(max_length=64, null=True, blank=True)
    original_article = models.CharField(max_length=64, null=True, blank=True)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    original_subtitle = models.CharField(max_length=255, null=True, blank=True)

    def get_original_title(self):
        return self.original_article + " " + self.original_title if self.original_article else self.original_title


class NamedTranslatableThing(NamedThing, TranslatedThing):
    is_translated = models.BooleanField()

    class Meta:
        abstract = True

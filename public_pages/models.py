from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Committee


class PublicPageGroup(models.Model):
    name = models.CharField(max_length=64)
    committees = models.ForeignKey(Committee, on_delete=PROTECT)

    def __str__(self):
        return self.name


class PublicPage(models.Model):
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    text = models.TextField()
    group = models.ForeignKey(PublicPageGroup, on_delete=PROTECT)
    show_title = models.BooleanField(default=True)
    only_for_logged_in = models.BooleanField(default=False)
    only_for_current_members = models.BooleanField(default=False)
    limited_to_committees = models.ManyToManyField(Committee, blank=True)


class FileUpload(models.Model):
    file = models.FileField(upload_to=".")

    def get_file_url(self):
        spl = self.file.name.split("/")
        return spl[-1]

    def get_full_url(self):
        return "/media/" + self.get_file_url()

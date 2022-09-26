from django.db import models

# Create your models here.
from django.db.models import PROTECT

from members.models import Committee

from django.conf import settings


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
    limited_to_committees = models.ManyToManyField(Committee)


class FileUpload(models.Model):
    file = models.FileField(upload_to="root/uploads/")
    name = models.CharField(max_length=64)

    def get_file_url(self):
        spl = self.file.name.split("/")
        return spl[-1]

    def get_full_url(self):
        return settings.STATIC_URL + "uploads/" + self.get_file_url()


class ExternalUpload(models.Model):
    external_name = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=64, unique=True)

    def get_file_url(self):
        return self.external_name

    def get_full_url(self):
        return settings.EXTERNAL_UPLOAD_URL_DOWNLOAD_PREFIX + self.external_name

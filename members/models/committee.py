from django.db import models


class Committee(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    active_member_committee = models.BooleanField()

    def __str__(self):
        return self.name

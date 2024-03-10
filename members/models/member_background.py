import sys

from django.db import models


class MemberBackground(models.Model):
    name = models.CharField(max_length=64)
    visual_name = models.CharField(max_length=64)
    old_str = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.visual_name

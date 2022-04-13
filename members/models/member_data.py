from django.db import models


class MemberData(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    addressLineOne = models.CharField(max_length=255)
    addressLineTwo = models.CharField(max_length=255)
    addressLineThree = models.CharField(max_length=255, blank=True)
    addressLineFour = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=64)
    student_number = models.CharField(max_length=32, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

from django.db import models


class MemberData(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    address_line_one = models.CharField(max_length=255)
    address_line_two = models.CharField(max_length=255)
    address_line_three = models.CharField(max_length=255, blank=True)
    address_line_four = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=64)
    student_number = models.CharField(max_length=32, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

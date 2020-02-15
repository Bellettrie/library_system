from django.db import models

# Create your models here.


class Member(models.Model):
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    addressLineOne = models.CharField(max_length=255)
    addressLineTwo = models.CharField(max_length=255)
    addressLineThree = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    studentNumber = models.CharField(max_length=32)
    notes = models.CharField(max_length=1023)

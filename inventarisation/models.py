from django.db import models

# Create your models here.
from django.db.models import PROTECT


class Inventarisation(models.Model):
    location = models.ForeignKey("works.Location", on_delete=PROTECT)
    dateTime = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
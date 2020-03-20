from django.db import models

# Create your models here.
from django.urls import reverse


class Holiday(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    starting_date = models.DateField()
    ending_date = models.DateField()

    def get_absolute_url(self):
        return reverse('holiday.view', kwargs={'pk': self.pk})
from django.db import models
from django.db.models import PROTECT


class Inventarisation(models.Model):
    location = models.ForeignKey("works.Location", on_delete=PROTECT)
    date_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            for inv in Inventarisation.objects.filter(location=self.location):
                if inv != self:
                    inv.is_active = False
                    inv.save()

    def get_absolute_url(self):
        return ""

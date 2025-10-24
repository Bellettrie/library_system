from django.db import models
from django.db.models import PROTECT

from creators.models import Creator, CreatorRole
from works.models.work import Work


class CreatorToWork(models.Model):
    creator = models.ForeignKey(Creator, on_delete=PROTECT)
    work = models.ForeignKey(Work, on_delete=PROTECT)
    number = models.IntegerField()

    class Meta:
        unique_together = ("creator", "work", "number")

    role = models.ForeignKey(CreatorRole, on_delete=PROTECT)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.work.update_listed_author()

from django.db import models

# Create your models here.
from django.db.models import CASCADE

from lendings.models import Lending
from members.models import Member


class Fine(models.Model):
    lending = models.ForeignKey(Lending, on_delete=CASCADE)
    paid = models.BooleanField(default=False)
    amount = models.IntegerField()
    return_date = models.DateTimeField()
    paid_on_date = models.DateTimeField(null=True)
    member = models.ForeignKey(Member, on_delete=CASCADE)
from django.db import models

# Create your models here.
from works.models import Creator


class CutterCodeRange(models.Model):
    from_affix = models.CharField(max_length=16)
    to_affix = models.CharField(max_length=16)
    number = models.CharField(max_length=16)
    generated_affix = models.CharField(max_length=20)

    @staticmethod
    def get_cutter_number(name: str):
        cutters = CutterCodeRange.objects.all().order_by("from_affix")
        result = None
        for cutter in cutters:
            if name.upper() < cutter.from_affix:
                return result
            result = cutter
        return result

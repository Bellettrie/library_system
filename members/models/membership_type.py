from django.db import models


class MembershipType(models.Model):
    name = models.CharField(max_length=64)
    visual_name = models.CharField(max_length=64)
    old_str = models.CharField(max_length=64, null=True, blank=True)
    needs_union_card = models.BooleanField(default=True)
    has_end_date = models.BooleanField(default=True)

    def __str__(self):
        return self.visual_name

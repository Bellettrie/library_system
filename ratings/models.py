from django.db import models

# Create your models here.
from django.db.models import CASCADE, SET_NULL

from members.models import Member
from works.models import Publication


class Rating(models.Model):
    publication = models.ForeignKey(Publication, on_delete=CASCADE)
    grade = models.IntegerField()
    member = models.ForeignKey(Member, null=True, on_delete=SET_NULL)
    date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.grade = min(10, max(1, self.grade))
        super().save(*args, **kwargs)


class Comment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=CASCADE, related_name='reaction')
    comment = models.TextField()
    author = models.CharField(max_length=32)
    accepted = models.BooleanField()
    date = models.DateTimeField(auto_now=True)

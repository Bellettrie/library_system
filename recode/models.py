from django.db import models

# Create your models here.
from django.db.models import CASCADE

from book_code_generation.models import BookCode
from works.models import Item


class Recode(BookCode):
    item = models.ForeignKey(Item, on_delete=CASCADE)
    book_code_extension = models.CharField(max_length=16)  # Where in the library is it?


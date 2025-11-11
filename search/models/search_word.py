from django.contrib.postgres.indexes import GinIndex
from django.db import models

from book_code_generation.helpers import normalize_str
from creators.models import Creator
from creators.procedures.get_all_author_aliases import get_all_author_aliases_by_ids
from series.models import Series
from tasks.models import Task

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from works.models import Work, WorkRelation, CreatorToWork, SubWork


class SearchWord(models.Model):
    word = models.CharField(max_length=255, db_index=True, unique=True)

    @staticmethod
    def get_word(word):
        return SearchWord.objects.get_or_create(word=word)[0]

    class Meta:
        indexes = (GinIndex(fields=["word"]),)  # add index

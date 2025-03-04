from django.core.management.base import BaseCommand

from creators.models import Creator
from members.models import Member
from search.models import WordMatch, SearchWord, SearchRecord
from series.models import Series
from works.models import Publication, SubWork


class Command(BaseCommand):
    help = 'Generate all search records'

    def handle(self, *args, **options):
        pubs = Publication.objects.all()
        SearchRecord.objects.all().delete()
        for pub in pubs:
            subworks = SubWork.objects.filter(workinpublication__publication=pub)
            author_words = ""
            sub_work_texts = ""
            for subwork in subworks:
                sub_work_texts += " " + subwork.all_title_words()
            sub_authors = ""
            for author in Creator.objects.filter(creatortowork__work__in=subworks):
                sub_authors = sub_authors + " " + author.get_name()

            authors = pub.get_authors()
            for author in authors:
                author_words = author_words + " " + author.creator.get_name()
            series_words = ""
            for ser in pub.all_series():
                if ser is not None:
                    series_words = series_words + " " + ser.all_title_words().lower()

            SearchRecord.objects.create(
                publication=pub,
                publication_title_text=pub.all_title_words().lower(),
                publication_sub_work_title_text=sub_work_texts.lower(),
                publication_sub_work_creator_text=sub_authors.lower(),
                publication_creator_text=author_words.lower(),
                publication_series_text=series_words
            )

        for creator in Creator.objects.all():
            SearchRecord.objects.create(
                creator=creator, creator_text=creator.get_name().lower())

        for member in Member.objects.all():
            SearchRecord.objects.create(member=member, member_text=member.name.lower())

        for series in Series.objects.all():
            pass
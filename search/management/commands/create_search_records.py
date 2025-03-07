from django.core.management.base import BaseCommand

from creators.models import Creator
from members.models import Member
from search.models import WordMatch, SearchWord, SearchRecord
from series.models import Series, WorkInSeries
from works.models import Publication, SubWork, Item, CreatorToWork


class Command(BaseCommand):
    help = 'Generate all search records'

    def handle(self, *args, **options):
        SearchRecord.objects.all().delete()
        SearchRecord.search_record_for_publication(Publication.objects.first())

        creator_words = dict()
        creator_parent_child = dict()
        creator_is_alias = dict()
        direct_creators = []
        creators = Creator.objects.all()
        for creator in creators:
            creator_words[creator.id] = creator_words.get(creator.id, "") + " "+creator.given_names + " " + creator.name
            if creator.is_alias_of_id is not None:
                creator_is_alias[creator.id] = creator.is_alias_of_id
                creator_parent_child[creator.is_alias_of_id] = creator_parent_child.get(creator.is_alias_of_id, []) + [
                    creator.id]
                creator_words[creator.is_alias_of_id] = creator_words.get(creator.is_alias_of_id,
                                                                          "") + " "+creator.given_names + " " + creator.name
            else:
                direct_creators.append(creator)

        def creator_names(crea):
            subs = creator_parent_child.get(crea, [])
            res = creator_words.get(crea)
            for child in creator_parent_child.get(crea, []):
                substrings, children = creator_names(child)
                res = res + " " + substrings
                subs += children
            return res, subs

        creator_indirect_alias = dict()
        creator_texts = dict()
        for creator in direct_creators:
            stringz, subs = creator_names(creator.id)
            for sub in subs:
                creator_indirect_alias[sub] = creator.id
            SearchRecord.objects.create(
                creator=creator, creator_text=stringz.lower())
            creator_texts[creator.id]=stringz.lower()
        series_creator_texts = dict()
        series_texts = dict()

        for crea in direct_creators:
            creator_indirect_alias[crea.id] = crea.id

        series_map = dict()
        for series in Series.objects.all():
            series_map[series.id] = series
        for series in Series.objects.prefetch_related("creatortoseries_set").all():
            sr = series
            sr_tx = ""
            sr_cx = ""
            while sr is not None:
                sr_tx += " "+ series.all_title_words()

                for crea in series.creatortoseries_set.all():
                    sr_cx += " "+creator_words[crea.creator_id]
                if sr.part_of_series is  None:
                    break
                sr = series_map[sr.part_of_series_id]


            series_texts[series.id] = sr_tx
            series_creator_texts[series.id] = sr_cx
            SearchRecord.objects.create(
                series=series, series_text=sr_tx.lower(), series_creator_text=sr_cx.lower())

        for publication in Publication.objects.all():
            SearchRecord.search_record_for_publication(publication)


        for member in Member.objects.all():
            SearchRecord.search_record_for_member(member)

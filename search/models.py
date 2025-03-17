from django.contrib.auth.models import User
from django.db import models

from django.db.models import CASCADE

from creators.models import Creator
from members.models import Member
from series.models import Series, WorkInSeries, CreatorToSeries
from works.models import Publication, SubWork, Item


class SearchRecord(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def search_record_for_author(creator: Creator, creator_dict: dict = None):
        SearchRecord.objects.filter(creator=creator).delete()
        start_crea = creator
        creator_name_text = ""
        starting_depth = 3
        depth = starting_depth
        while True:
            creator_name_text += " "+ creator.given_names + " " + creator.name

            if start_crea.is_alias_of_id is None or depth < 0:
                break
            if creator_dict:
                start_crea = creator_dict[start_crea.is_alias_of_id]
            else:
                start_crea = creator.is_alias_of
            depth -= 1
        SearchRecord.objects.create(creator=creator, creator_text=creator_name_text.lower(),
                                    hidden=not (depth < 0 or depth == starting_depth))

    @staticmethod
    def search_record_for_series(series: Series, series_dict: dict = None, creator_dict: dict = None):
        SearchRecord.objects.filter(series=series).delete()
        series_text = series.all_title_words() + " " + (series.search_words or "")
        series_creator_text = ""
        crs = SearchRecord.objects.filter(
            creator_id__in=map((lambda i: i.creator_id), series.creatortoseries_set.all())).all()
        for cr in crs:
            series_creator_text += " " + cr.creator_text
        series_parents_text = ""
        sr = series
        while sr.part_of_series_id is not None:
            if series_dict is not None:
                sr = series_dict[sr.part_of_series_id]
            else:
                sr = sr.part_of_series
            series_parents_text += " " + sr.all_title_words()
            crs = SearchRecord.objects.filter(
                creator_id__in=map((lambda i: i.creator_id), sr.creatortoseries_set.all())).all()
            for cr in crs:
                series_creator_text += " " + cr.creator_text
        result_priority=1.2
        if not series.is_translated:
            result_priority= 1.3
        SearchRecord.objects.create(series=series, search_words=series.search_words or "", series_text=series_text.lower(), series_creator_text=series_creator_text.lower(), series_parents_text=series_parents_text.lower(), result_priority=result_priority)

    @staticmethod
    def search_record_for_member(member: Member):
        SearchRecord.objects.filter(member=member).delete()

        SearchRecord.objects.create(member=member, member_text=member.name + " " + member.student_number, result_priority=1.4)

    @staticmethod
    def search_record_for_publication(pub: Publication):
        SearchRecord.objects.filter(item__in=pub.item_set.all()).delete()
        publication_title_text = pub.all_title_words(titles=["title"])
        publication_title_secondary_text = pub.all_title_words(titles=["original_subtitle", "original_title","original_subtitle"])

        publication_creator_text = ""

        crs = SearchRecord.objects.filter(
            creator_id__in=map((lambda i: i.creator_id), pub.creatortowork_set.all())).all()
        for cr in crs:
            publication_creator_text += " " + cr.creator_text
        publication_series_text = ""
        srs = SearchRecord.objects.filter(
            series_id__in=map((lambda i: i.part_of_series), pub.workinseries_set.all())).all()
        for sr in srs:
            publication_creator_text += " " + sr.series_creator_text
            publication_series_text += " " + sr.series_text + " " + sr.series_parents_text

        publication_sub_work_creator_text = ""
        publication_sub_work_title_text = ""
        for sub in SubWork.objects.filter(workinpublication__publication
                                          =pub).all():
            publication_sub_work_title_text += " " + sub.all_title_words()

            crs = SearchRecord.objects.filter(
                creator_id__in=map((lambda i: i.creator_id), sub.creatortowork_set.all())).all()
            for cr in crs:
                publication_sub_work_creator_text += " " + cr.creator_text

        sco = 1
        if not pub.is_translated:
            sco += 0.1
        for item in pub.item_set.all():
            SearchRecord.objects.create(item_id=item.id, publication_title_text=publication_title_text,
                                        publication_series_text=publication_series_text,
                                        publication_sub_work_title_text=publication_sub_work_title_text,
                                        publication_creator_text=publication_creator_text,
                                        publication_sub_work_creator_text=publication_sub_work_creator_text,
                                        publication_title_secondary_text=publication_title_secondary_text,
                                        result_priority=sco)

    item = models.ForeignKey(Item, on_delete=CASCADE, null=True, blank=True, db_index=True)
    series = models.ForeignKey(Series, on_delete=CASCADE, null=True, blank=True, db_index=True)
    creator = models.ForeignKey(Creator, on_delete=CASCADE, null=True, blank=True, db_index=True)
    member = models.ForeignKey(Member, on_delete=CASCADE, null=True, blank=True, db_index=True)

    search_words = models.TextField(null=False, default="")


    publication_title_text = models.TextField(null=False, default="")
    publication_title_secondary_text = models.TextField(null=False, default="")

    publication_series_text = models.TextField(null=False, default="")
    publication_sub_work_title_text = models.TextField(null=False, default="")
    publication_creator_text = models.TextField(null=False, default="")
    publication_sub_work_creator_text = models.TextField(null=False, default="")

    member_text = models.TextField(null=False, default="")
    member_is_current_member = models.BooleanField(null=True, blank=True)

    creator_text = models.TextField(null=False, default="")

    series_text = models.TextField(null=False, default="")  # All words through the
    series_parents_text = models.TextField(null=False, default="")  # All words through the

    series_creator_text = models.TextField(null=False, default="")  # All words through the
    hidden = models.BooleanField(default=False)

    result_priority = models.FloatField(default=1)

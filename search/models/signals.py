from datetime import timedelta
from typing import List

from creators.models import Creator
from creators.procedures.get_all_author_aliases import get_all_author_aliases_by_ids
from search.models import WordMatch

from tasks.models import Task

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from utils.time import get_now
from works.models import Work, WorkRelation, CreatorToWork


class UpdateWorks:
    def __init__(self, works: List[Work]):
        self.work_ids = list(map(lambda work: work.id, works))

    def exec(self):
        works = Work.objects.filter(id__in=self.work_ids)
        for work in works:
            WordMatch.create_all_for(work)


@receiver(post_save, sender=Work)
def work_updated_receiver(sender, instance: Work, created, **kwargs):
    res_works = get_works_from_ids([instance.id])
    for work in res_works:
        WordMatch.create_all_for(work)


def work_relation_updated(ids):
    res_works = get_works_from_ids(ids)
    print(ids, res_works)
    for work in res_works:
        WordMatch.create_all_for(work)


@receiver(pre_save, sender=WorkRelation)
def work_relation_updated_presave(sender, instance: WorkRelation, **kwargs):
    prevs = WorkRelation.objects.filter(id=instance.id)
    if len(prevs) == 0:
        return
    prev = prevs[0]
    if instance.from_work_id == prev.from_work_id and instance.to_work_id == prev.to_work_id:
        return
    res_works = get_works_from_ids([prev.from_work_id, prev.to_work_id])
    for work in res_works:
        WordMatch.create_all_for(work)

    Task.objects.create(task_name="update-works-work-relation-update-rels", task_object=UpdateWorks(list(res_works)),
                        next_datetime=get_now() + timedelta(seconds=5))


@receiver(post_save, sender=WorkRelation)
def work_relation_updated_receiver(sender, instance: WorkRelation, **kwargs):
    ids = [instance.from_work.id, instance.to_work.id]
    work_relation_updated(ids)


def creator_updated(instance: Creator):
    creators = get_all_author_aliases_by_ids([instance.id])
    ids = []
    for creator in creators:
        ids.append(creator.id)
    creator_to_works = CreatorToWork.objects.filter(creator_id__in=ids)
    ids = []
    for c2w in creator_to_works:
        ids.append(c2w.work_id)
    res_works = get_works_from_ids(ids)

    return res_works


@receiver(pre_save, sender=Creator)
def creator_updated_receiver_presave(sender, instance: Creator, **kwargs):
    crea = Creator.objects.filter(id=instance.id)
    if len(crea) == 0:
        return
    if crea[0].is_alias_of_id == instance.is_alias_of_id:
        return
    res_works = creator_updated(crea[0].is_alias_of)
    Task.objects.create(task_name="update-creator-update-alias", task_object=UpdateWorks(list(res_works)),
                        next_datetime=get_now() + timedelta(seconds=5))


@receiver(post_save, sender=Creator)
def creator_updated_receiver(sender, instance: Creator, created, **kwargs):
    res_works = creator_updated(instance)
    for work in res_works:
        WordMatch.create_all_for(work)


@receiver(pre_save, sender=CreatorToWork)
def creator_to_work_updated_receiver_presave(sender, instance: CreatorToWork, **kwargs):
    prevs = CreatorToWork.objects.filter(id=instance.id)
    if len(prevs) == 0:
        return
    prev = prevs[0]
    if instance.work_id == prev.work_id:
        return
    res_works = get_works_from_ids([prev.work_id])

    for work in res_works:
        WordMatch.create_all_for(work)

    Task.objects.create(task_name="update-works-creator-to-work-prevs", task_object=UpdateWorks(list(res_works)),
                        next_datetime=get_now() + timedelta(seconds=5))


@receiver(post_save, sender=CreatorToWork)
def creator_to_work_updated_receiver(sender, instance: CreatorToWork, **kwargs):
    res_works = get_works_from_ids([instance.work.id])

    for work in res_works:
        WordMatch.create_all_for(work)


@receiver(pre_delete, sender=Work)
def work_deleted_receiver(sender, instance: Work, **kwargs):
    WordMatch.objects.filter(publication=instance).delete()

    res_works = get_works_from_ids([instance.id])
    wks = []
    for res_work in res_works:
        if instance.id != res_work.id:
            wks.append(res_work)
    Task.objects.create(task_name="update-works-work-delete", task_object=UpdateWorks(wks))


# The deletes should be deferred, so they are executed *after* the entities are gone.
@receiver(pre_delete, sender=WorkRelation)
def work_relation_deleted_receiver(sender, instance: WorkRelation, **kwargs):
    in_ids = [instance.to_work.id, instance.from_work.id]
    res_works = get_works_from_ids(in_ids)
    for work in res_works:
        WordMatch.create_all_for(work)

    Task.objects.create(task_name="update-works-work-relation-delete", task_object=UpdateWorks(list(res_works)))


@receiver(pre_delete, sender=Creator)
def creator_deleted_receiver(sender, instance: Creator, **kwargs):
    creators = get_all_author_aliases_by_ids([instance.id])
    ids = []
    for creator in creators:
        ids.append(creator.id)
    creator_to_works = CreatorToWork.objects.filter(creator_id__in=ids)
    in_ids = []
    for c2w in creator_to_works:
        in_ids.append(c2w.work.id)

    res_works = get_works_from_ids(in_ids)

    for work in res_works:
        WordMatch.create_all_for(work)

    Task.objects.create(task_name="update-works-creator-delete", task_object=UpdateWorks(list(res_works)))


@receiver(pre_delete, sender=CreatorToWork)
def creator_to_work_deleted_receiver(sender, instance: CreatorToWork, **kwargs):
    res_works = get_works_from_ids([instance.work.id])

    Task.objects.create(task_name="update-works-creator_to_work-delete", task_object=UpdateWorks(list(res_works)))


def get_works_from_ids(in_ids):
    works = WorkRelation.RelationTraversal.for_search_words_inverse(in_ids)
    ids = in_ids
    for work in works:
        ids.append(work.from_work_id)
        ids.append(work.to_work_id)

    return Work.objects.filter(pk__in=set(ids))

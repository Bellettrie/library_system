from typing import List

from creators.models import Creator
from creators.procedures.get_all_author_aliases import get_all_author_aliases_by_ids
from search.models import WordMatch

from tasks.models import Task

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from works.models import Work, WorkRelation, CreatorToWork


class UpdateWorks:
    def __init__(self, works: List[Work]):
        self.works = works

    def exec(self):
        for work in self.works:
            WordMatch.create_all_for(work)


@receiver(post_save, sender=Work)
def work_updated_receiver(sender, instance: Work, created, **kwargs):
    res_works = get_works_from_ids([instance.id])
    for work in res_works:
        WordMatch.create_all_for(work)


@receiver(post_save, sender=WorkRelation)
def work_relation_updated_receiver(sender, instance: WorkRelation, created, **kwargs):
    res_works = get_works_from_ids([instance.from_work.id, instance.to_work.id])

    for work in res_works:
        WordMatch.create_all_for(work)


@receiver(post_save, sender=Creator)
def creator_updated_receiver(sender, instance: Creator, created, **kwargs):
    creators = get_all_author_aliases_by_ids([instance.id])
    ids = []
    for creator in creators:
        ids.append(creator.id)
    creator_to_works = CreatorToWork.objects.filter(creator_id__in=ids)
    ids = []
    for c2w in creator_to_works:
        ids.append(c2w.work_id)
    res_works = get_works_from_ids(ids)

    for work in res_works:
        WordMatch.create_all_for(work)


@receiver(post_save, sender=CreatorToWork)
def creator_to_work_updated_receiver(sender, instance: CreatorToWork, **kwargs):
    res_works = get_works_from_ids([instance.work.id])

    for work in res_works:
        WordMatch.create_all_for(work)


@receiver(pre_delete, sender=Work)
def work_deleted_receiver(sender, instance: Work, **kwargs):
    res_works = get_works_from_ids([instance.id])
    wks = []
    for res_work in res_works:
        if instance.id != res_work.id:
            wks.append(res_work)
    Task.objects.create(task_name="update-works-work-delete", task_object=UpdateWorks(wks))


# The deletes should be deferred, so they are executed *after* the entities are gone.
@receiver(pre_delete, sender=WorkRelation)
def work_relation_deleted_receiver(sender, instance: WorkRelation, **kwargs):
    in_ids = [instance.to_work, instance.from_work]
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

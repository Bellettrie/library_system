from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from creators.models import Creator
from search.models import WordMatch
from works.models import Work, WorkRelation, CreatorToWork


@receiver(post_save, sender=Work)
def work_updated_receiver(sender, instance, created, **kwargs):
    WordMatch.create_all_for(instance)


@receiver(post_save, sender=WorkRelation)
def work_relation_updated_receiver(sender, instance, created, **kwargs):
    WordMatch.create_all_for(instance.from_work)
    WordMatch.create_all_for(instance.to_work)


@receiver(post_save, sender=Creator)
def creator_updated_receiver(sender, instance, created, **kwargs):
    base_works = Work.objects.filter(creatortowork__creator=instance)
    ids = []
    for base_work in base_works:
        ids.append(base_work.id)
    works = WorkRelation.RelationTraversal.for_search_words_inverse(ids)
    for work in works:
        WordMatch.create_all_for(work)


@receiver(post_save, sender=CreatorToWork)
def creator_to_work_updated_receiver(sender, instance, **kwargs):
    works = Work.objects.filter(creatortowork=instance)
    ids = []
    for work in works:
        ids.append(work.id)

    works = WorkRelation.RelationTraversal.for_search_words_inverse(ids)
    for work in works:
        WordMatch.create_all_for(work)


@receiver(pre_delete, sender=WorkRelation)
def work_relation_deleted_receiver(sender, instance, **kwargs):
    pass
    #TODO: Implement me


@receiver(pre_delete, sender=Creator)
def creator_deleted_receiver(sender, instance, **kwargs):
    pass
    #TODO: Implement me


@receiver(pre_delete, sender=Creator)
def creator_to_work_deleted_receiver(sender, instance, **kwargs):
    pass
    #TODO: Implement me
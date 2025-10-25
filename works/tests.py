import time
from typing import List

from django.db.models.query import RawQuerySet
from django.test import TestCase
from works.models import Publication, Item, Category, Location, ItemType, WorkRelation


def create_work(title: str):
    return Publication.objects.create(title=title,
                                      is_translated=False,
                                      date_added='1900-01-01',
                                      hidden=False,
                                      old_id=0
                                      )


def item_create(title: str, location: Location):
    work = create_work(title)
    return Item.objects.create(publication=work, location=location, hidden=False)


def location_create(location_name: str, category_name: str, item_type: ItemType):
    category = Category.objects.create(name=category_name, item_type=item_type)
    return Location.objects.create(name=location_name, category=category)


class WorkTests(TestCase):
    def setUp(self):
        self.work1 = create_work('Work')
        self.work2 = create_work('Work2')
        self.work3 = create_work('Work3')
        self.work4 = create_work('Work4')
        self.work5 = create_work('Work5')

        self.work6 = create_work('Work6')
        self.work7 = create_work('Work7')
        self.work8 = create_work('Work8')
        self.rel1 = WorkRelation.objects.create(source_work=self.work1, target_work=self.work2,
                                                relation_kind=WorkRelation.RelationType.sub_work_of, relation_index=1)
        self.rel2 = WorkRelation.objects.create(source_work=self.work2, target_work=self.work3,
                                                relation_kind=WorkRelation.RelationType.sub_work_of, relation_index=2)
        self.rel3 = WorkRelation.objects.create(source_work=self.work4, target_work=self.work2,
                                                relation_kind=WorkRelation.RelationType.sub_work_of, relation_index=3)
        self.rel4 = WorkRelation.objects.create(source_work=self.work4, target_work=self.work5,
                                                relation_kind=WorkRelation.RelationType.sub_work_of, relation_index=4)
        self.rel5 = WorkRelation.objects.create(source_work=self.work1, target_work=self.work5,
                                                relation_kind=WorkRelation.RelationType.part_of_series, relation_index=1)

    def assertSameRelations(self, first: RawQuerySet, second: List[WorkRelation]):
        fst_set = set(map(lambda x: x.id, first))
        snd_set = set(map(lambda x: x.id, second))
        self.assertEqual(len(first), len(second))
        self.assertEqual(fst_set, snd_set)

    def test_relations_2_jump(self):
        rels = WorkRelation.traverse_relations([self.work1.id], [1], [])
        self.assertSameRelations(rels, [self.rel1, self.rel2])

    def test_relations_2_jump_multiple(self):
        rels = WorkRelation.traverse_relations([self.work1.id], [1, 2], [])
        self.assertSameRelations(rels, [self.rel1, self.rel2, self.rel5])

    def test_relations_1_jump(self):
        rels = WorkRelation.traverse_relations([self.work2.id], [1], [])
        self.assertSameRelations(rels, [self.rel2])

    def test_relations_reverse(self):
        rels = WorkRelation.traverse_relations([self.work2.id], [], [1])
        self.assertSameRelations(rels, [self.rel1, self.rel3])

    def test_relations_bidirectional(self):
        rels = WorkRelation.traverse_relations([self.work2.id], [1], [1])
        self.assertSameRelations(rels, [self.rel1, self.rel2, self.rel3, self.rel4])


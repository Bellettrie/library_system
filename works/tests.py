import time

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
        self.w1 = WorkRelation.objects.create(work=self.work1, relates_to=self.work2,
                                              relation_type=WorkRelation.RelationType.sub_work, number_in_relation=1)
        self.w2 = WorkRelation.objects.create(work=self.work2, relates_to=self.work3,
                                              relation_type=WorkRelation.RelationType.sub_work, number_in_relation=2)
        self.w3 = WorkRelation.objects.create(work=self.work4, relates_to=self.work2,
                                              relation_type=WorkRelation.RelationType.sub_work, number_in_relation=3)
        self.w4 = WorkRelation.objects.create(work=self.work4, relates_to=self.work5,
                                              relation_type=WorkRelation.RelationType.sub_work, number_in_relation=4)

        self.w5 = WorkRelation.objects.create(work=self.work1, relates_to=self.work5,
                                              relation_type=WorkRelation.RelationType.series, number_in_relation=1)

    def test_relations_2_jump(self):
        rels = WorkRelation.recursive_work_relations_from([self.work1.id], [1], [])
        self.assertEqual(len(rels), 2)

    def test_relations_2_jump_multiple(self):
        rels = WorkRelation.recursive_work_relations_from([self.work1.id], [1, 2], [])
        self.assertEqual(len(rels), 3)

    def test_relations_1_jump(self):
        rels = WorkRelation.recursive_work_relations_from([self.work2.id], [1], [])
        self.assertEqual(len(rels), 1)

    def test_relations_reverse(self):
        rels = WorkRelation.recursive_work_relations_from([self.work2.id], [], [1])
        self.assertEqual(len(rels), 2)

    def test_relations_bidirectional(self):
        rels = WorkRelation.recursive_work_relations_from([self.work2.id], [1], [1])
        self.assertEqual(len(rels), 4)

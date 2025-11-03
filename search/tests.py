from django.test import TestCase

from creators.models import Creator, CreatorRole
from search.models import WordMatch, SearchWord
from works.models import WorkRelation, CreatorToWork
from works.tests import create_work


# Create your tests here.

class WorkRelationTests(TestCase):
    def setUp(self):
        self.work1 = create_work('Work')
        self.work2 = create_work('Work2')
        self.work3 = create_work('Work3')

        self.rel1 = WorkRelation.objects.create(from_work=self.work2, to_work=self.work1,
                                                relation_kind=WorkRelation.RelationKind.sub_work_of, relation_index=1)
        self.rel2 = WorkRelation.objects.create(from_work=self.work1, to_work=self.work3,
                                                relation_kind=WorkRelation.RelationKind.part_of_series, relation_index=2)
        crea = Creator.objects.create(given_names="Bob", name="Bouwer")
        Creator.objects.create(given_names="Bob", name="Builder", is_alias_of=crea)
        role = CreatorRole.objects.create(name='builder')
        CreatorToWork.objects.create(creator=crea, work=self.work3, number=1, role=role )

    def test_word_match_gen(self):
        WordMatch.objects.all().delete()
        WordMatch.create_all_for(self.work1)
        wms = WordMatch.objects.all()
        words = {}
        for word in SearchWord.objects.all():
            words[word.word] = word
        matches = [WordMatch(word=words["WORK"], publication=self.work1, type='TITLE'),
                   WordMatch(word=words["WORK2"], publication=self.work1, type='SUBWORK'),
                   WordMatch(word=words["WORK3"], publication=self.work1, type='SERIES'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOUWER"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BUILDER"], publication=self.work1, type='CREATOR')]

        self.assertEqual(len(matches), len(wms))
        for match in matches:
            mtc = False
            for wm in wms:
                if wm.word == match.word and wm.publication == match.publication and wm.type == match.type:
                    mtc = True
            self.assertTrue(mtc, f"{match} not found in result set {wms}")

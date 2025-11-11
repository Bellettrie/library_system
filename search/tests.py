from django.test import TestCase

from creators.models import Creator, CreatorRole
from search.models import WordMatch, SearchWord
from works.models import WorkRelation, CreatorToWork
from works.tests import create_work


class WorkRelationTests(TestCase):
    def setUp(self):
        self.work1 = create_work('Work')
        self.work2 = create_work('Work2')
        self.work3 = create_work('Work3')

        self.rel1 = WorkRelation.objects.create(from_work=self.work2, to_work=self.work1,
                                                relation_kind=WorkRelation.RelationKind.sub_work_of, relation_index=1)
        self.rel2 = WorkRelation.objects.create(from_work=self.work1, to_work=self.work3,
                                                relation_kind=WorkRelation.RelationKind.part_of_series,
                                                relation_index=2)
        crea = Creator.objects.create(given_names="Bob", name="Bouwer")
        self.crea2 = Creator.objects.create(given_names="Bob", name="Builder", is_alias_of=crea)
        role = CreatorRole.objects.create(name='builder')
        CreatorToWork.objects.create(creator=crea, work=self.work3, number=1, role=role)

    def matches_equal(self, matches):
        wms = WordMatch.objects.all()
        self.assertEqual(len(matches), len(wms))
        for match in matches:
            mtc = False
            for wm in wms:
                if wm.word == match.word and wm.publication == match.publication and wm.type == match.type:
                    mtc = True
            self.assertTrue(mtc, f"{match} not found in result set {wms}")

    def get_all_words(self):
        words = {}
        for word in SearchWord.objects.all():
            words[word.word] = word
        return words

    def test_word_match_gen(self):
        WordMatch.objects.all().delete()
        WordMatch.create_all_for(self.work1)
        words = self.get_all_words()
        matches = [WordMatch(word=words["WORK"], publication=self.work1, type='TITLE'),
                   WordMatch(word=words["WORK2"], publication=self.work1, type='SUBWORK'),
                   WordMatch(word=words["WORK3"], publication=self.work1, type='SERIES'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOUWER"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BUILDER"], publication=self.work1, type='CREATOR')]

        self.matches_equal(matches)

    def test_word_match_auto_update_based_on_work(self):
        WordMatch.objects.all().delete()
        self.work1.title = "DORK"
        self.work1.save()

        words = self.get_all_words()
        matches = [WordMatch(word=words["DORK"], publication=self.work1, type='TITLE'),
                   WordMatch(word=words["WORK2"], publication=self.work1, type='SUBWORK'),
                   WordMatch(word=words["WORK3"], publication=self.work1, type='SERIES'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOUWER"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BUILDER"], publication=self.work1, type='CREATOR')]

        self.matches_equal(matches)

    def test_word_match_auto_update_based_on_subwork(self):
        WordMatch.objects.all().delete()
        self.work2.title = "DORK"
        self.work2.save()
        WordMatch.objects.exclude(publication=self.work1).delete()
        words = self.get_all_words()
        matches = [WordMatch(word=words["WORK"], publication=self.work1, type='TITLE'),
                   WordMatch(word=words["DORK"], publication=self.work1, type='SUBWORK'),
                   WordMatch(word=words["WORK3"], publication=self.work1, type='SERIES'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOUWER"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BUILDER"], publication=self.work1, type='CREATOR')]
        self.matches_equal(matches)

    def test_word_match_auto_update_based_on_creator(self):
        WordMatch.objects.all().delete()
        self.crea2.given_names = "DERP"
        self.crea2.save()
        WordMatch.objects.exclude(publication=self.work1).delete()
        words = self.get_all_words()
        matches = [WordMatch(word=words["WORK"], publication=self.work1, type='TITLE'),
                   WordMatch(word=words["WORK2"], publication=self.work1, type='SUBWORK'),
                   WordMatch(word=words["WORK3"], publication=self.work1, type='SERIES'),
                   WordMatch(word=words["DERP"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOUWER"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BUILDER"], publication=self.work1, type='CREATOR')]
        self.matches_equal(matches)

    def test_word_match_auto_update_based_on_creator_to_work(self):
        WordMatch.objects.all().delete()
        work4 = create_work("work4")
        WorkRelation.objects.create(from_work=self.work1, to_work=work4,
                                                relation_kind=WorkRelation.RelationKind.part_of_series,
                                                relation_index=2)
        WordMatch.objects.exclude(publication=self.work1).delete()
        words = self.get_all_words()
        matches = [WordMatch(word=words["WORK"], publication=self.work1, type='TITLE'),
                   WordMatch(word=words["WORK2"], publication=self.work1, type='SUBWORK'),
                   WordMatch(word=words["WORK3"], publication=self.work1, type='SERIES'),
                   WordMatch(word=words["WORK4"], publication=self.work1, type='SERIES'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOUWER"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BOB"], publication=self.work1, type='CREATOR'),
                   WordMatch(word=words["BUILDER"], publication=self.work1, type='CREATOR')]
        self.matches_equal(matches)

from django.db import models
from django.db.models import CASCADE

from creators.models import Creator
from creators.procedures.get_all_author_aliases import get_all_author_aliases_by_ids
from search.models.helpers import get_word_from_set, get_words_in_str
from search.models.search_word import SearchWord
from works.models import Work, WorkRelation


class WordMatch(models.Model):
    word = models.ForeignKey(SearchWord, on_delete=CASCADE, db_index=True)
    publication = models.ForeignKey(Work, on_delete=CASCADE)
    type = models.CharField(max_length=8, default="TITLE", db_index=True)

    def __hash__(self):
        return hash((self.word_id, self.publication_id, self.type))

    def __str__(self):
        return f"{self.word.word} {self.publication} {self.type}"

    @staticmethod
    def create_all_for(work: Work, words=None):
        if words is None:
            words = {}

        WordMatch.objects.filter(publication=work).delete()

        # start with all the words directly belonging to the title etc. of the work
        matches = WordMatch.get_wordmatches_for_work(words, work, work)
        related_works = [work]

        # Now traverse the tree to find
        work_relations = WorkRelation.RelationTraversal.for_search_words([work.id])

        for relation in work_relations:
            if relation.relation_kind == WorkRelation.RelationKind.sub_work_of:
                relation_kind = "SUBWORK"
                related_work = relation.from_work
            elif relation.relation_kind == WorkRelation.RelationKind.part_of_series:
                relation_kind = "SERIES"
                related_work = relation.to_work
            elif relation.relation_kind == WorkRelation.RelationKind.part_of_secondary_series:
                relation_kind = "SERIES"
                related_work = relation.to_work
            else:
                # We don't know in which direction it was picked up, so we can't use it.
                continue

            related_works.append(related_work)

            for match in WordMatch.get_wordmatches_for_work(words, work, related_work, relation_kind):
                matches.append(match)

        creator_ids = []
        for creator in Creator.objects.filter(creatortowork__work__in=related_works).all():
            creator_ids.append(creator.id)

        creators = get_all_author_aliases_by_ids(creator_ids)
        for creator in creators:
            for word in get_words_in_str(creator.given_names):
                matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type="CREATOR"))
            for word in get_words_in_str(creator.name):
                matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type="CREATOR"))
        matches = list(set(matches))
        WordMatch.objects.bulk_create(matches)

        # TODO: These two will be history when the subworks and series are migrated.
        return words

    @staticmethod
    def get_wordmatches_for_work(words, pub: Work, work_for_words: Work, role="TITLE"):
        matches = []
        for word in get_words_in_str(work_for_words.article):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=pub, type=role))
        for word in get_words_in_str(work_for_words.title):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=pub, type=role))
        for word in get_words_in_str(work_for_words.sub_title):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=pub, type=role))
        for word in get_words_in_str(work_for_words.original_article):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=pub, type=role))
        for word in get_words_in_str(work_for_words.original_title):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=pub, type=role))
        for word in get_words_in_str(work_for_words.original_subtitle):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=pub, type=role))
        return matches

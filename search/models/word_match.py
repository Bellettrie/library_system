from django.db import models
from django.db.models import CASCADE

from creators.models import Creator
from creators.procedures.get_all_author_aliases import get_all_author_aliases_by_ids
from search.models.helpers import get_word_from_set, get_words_in_str
from search.models.search_word import SearchWord
from series.models import Series
from works.models import Work, WorkRelation


class WordMatch(models.Model):
    word = models.ForeignKey(SearchWord, on_delete=CASCADE, db_index=True)
    publication = models.ForeignKey(Work, on_delete=CASCADE)
    type = models.CharField(max_length=8, default="TITLE", db_index=True)

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

        WordMatch.objects.bulk_create(matches)

        # TODO: These two will be history when the subworks and series are migrated.
        AuthorWordMatch.get_all_for_authors(work, words)
        SeriesWordMatch.get_all_for_serieses(work, words)
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


class AuthorWordMatch(WordMatch):
    creator = models.ForeignKey(Creator, on_delete=CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "AUTHOR"

    @staticmethod
    def get_all_for_author(work: Work, creator: Creator, words):
        names = set()
        for creator in get_all_author_aliases_by_ids([creator.id]):
            for name in get_words_in_str(creator.name):
                AuthorWordMatch.objects.create(word=get_word_from_set(name, words), publication=work, creator=creator)
            for name in get_words_in_str(creator.given_names):
                AuthorWordMatch.objects.create(word=get_word_from_set(name, words), publication=work, creator=creator)
        return names

    @staticmethod
    def get_all_for_authors(work: Work, words=None):
        if words is None:
            words = {}
            for word in SearchWord.objects.all():
                words[word.word] = word
        for creator in work.get_authors():
            AuthorWordMatch.get_all_for_author(work, creator.creator, words)

    @staticmethod
    def author_rename(author: Creator):
        for pub in author.get_all_publications():
            WordMatch.create_all_for(pub)


class SeriesWordMatch(WordMatch):
    series = models.ForeignKey(Series, on_delete=CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "SERIES"

    @staticmethod
    def get_all_for_series(work: Work, series: Series, words):
        if series is None:
            return
        for word in get_words_in_str(series.article):
            SeriesWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, series=series)
        for word in get_words_in_str(series.original_article):
            SeriesWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, series=series)
        for word in get_words_in_str(series.title):
            SeriesWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, series=series)
        for word in get_words_in_str(series.sub_title):
            SeriesWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, series=series)
        for word in get_words_in_str(series.original_title):
            SeriesWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, series=series)
        for word in get_words_in_str(series.original_subtitle):
            SeriesWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, series=series)

    @staticmethod
    def get_all_for_serieses(work: Work, words=None):
        if words is None:
            words = {}
            for word in SearchWord.objects.all():
                words[word.word] = word
        ser = list(work.workinseries_set.all())
        handled = []
        for series in ser:
            if series in handled:
                continue
            SeriesWordMatch.get_all_for_series(work, series.part_of_series, words)
            if not series.part_of_series:
                continue
            if series.part_of_series.part_of_series:
                ser.append(series.part_of_series)
            handled.append(series)

    @staticmethod
    def series_rename(series: Series):
        words = {}
        for word in SearchWord.objects.all():
            words[word.word] = word

        serieses = [series]
        for s in serieses:
            for pub in Work.objects.filter(workinseries__part_of_series_id=s.pk):
                WordMatch.create_all_for(pub, words)
            for ss in Series.objects.filter(part_of_series_id=s.pk):
                serieses.append(ss)

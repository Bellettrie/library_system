from django.contrib.postgres.indexes import GinIndex
from django.db import models
# Create your models here.
from django.db.models import CASCADE

from book_code_generation.helpers import normalize_str
from creators.models import Creator
from series.models import Series
from works.models import Publication, Work, WorkRelation


class SearchWord(models.Model):
    word = models.CharField(max_length=255, db_index=True, unique=True)

    @staticmethod
    def get_word(word):
        return SearchWord.objects.get_or_create(word=word)[0]

    class Meta:
        indexes = (GinIndex(fields=["word"]),)  # add index


def get_word_from_set(word: str, word_set: dict):
    """
        Given a dictionary of string -> SearchWord, get the word from the dictionary. This is an optimization for the search word generation function.
    """
    word = word.upper()
    w = word_set.get(word, None)
    if w is not None:
        return w

    word_set[word] = SearchWord.get_word(word)
    return word_set[word]


def clean_word(string):
    """
    Remove anything not alphanumeric from word.
    """
    string = normalize_str(string)
    return "".join(ch for ch in string if ch.isalnum() or ch == "*").upper()


def get_words_in_str(string):
    """
        Split string into spaces and
    """
    if string is None:
        return []
    string = string.replace("'", " ")
    z = string.strip().split(" ")
    result = []
    for w in z:
        w = clean_word(w)
        if len(w) > 1:
            result.append(w)
    return result


class WordMatch(models.Model):
    word = models.ForeignKey(SearchWord, on_delete=CASCADE, db_index=True)
    publication = models.ForeignKey(Publication, on_delete=CASCADE)
    type = models.CharField(max_length=8, default="TITLE", db_index=True)

    @staticmethod
    def create_all_for(work: Publication, words=None):
        if words is None:
            words = {}

        WordMatch.objects.filter(publication=work).delete()

        matches = WordMatch.get_wordmatches_for_work(words, work, work)

        work_relations = WorkRelation.RecursiveRelations.search_words_relations(work.id)
        works_for_creators = [work]

        for rel in work_relations:
            if rel.relation_type == WorkRelation.RelationType.sub_work:
                typ = "SUBWORK"
                nd = rel.work
            elif rel.relation_type == WorkRelation.RelationType.series:
                typ = "SERIES"
                nd = rel.relates_to
            else:
                # We don't know in which direction it was picked up, so we can't use it.
                continue
            works_for_creators.append(nd)
            for mtz in WordMatch.get_wordmatches_for_work(words, work, nd, typ):
                matches.append(mtz)

        for creator in Creator.objects.filter(creatortowork__work__in=works_for_creators).all():
            for word in get_all_given_names(creator):
                matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type="AUTHOR"))
        WordMatch.objects.bulk_create(matches)

        # TODO: These two will be history when the series are also migrated.
        AuthorWordMatch.get_all_for_authors(work, words)
        SeriesWordMatch.get_all_for_serieses(work, words)

        return words

    @staticmethod
    def get_wordmatches_for_work(words, work: Publication, work_for_words: Publication, role="TITLE"):
        matches = []
        for word in get_words_in_str(work_for_words.article):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type=role))
        for word in get_words_in_str(work_for_words.title):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type=role))
        for word in get_words_in_str(work_for_words.sub_title):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type=role))
        for word in get_words_in_str(work_for_words.original_article):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type=role))
        for word in get_words_in_str(work_for_words.original_title):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type=role))
        for word in get_words_in_str(work_for_words.original_subtitle):
            matches.append(WordMatch(word=get_word_from_set(word, words), publication=work, type=role))
        return matches


def get_all_given_names(creator: Creator):
    names = set()
    creators = set()
    handle = [creator]
    for crea in handle:
        if crea in creators:
            continue
        if crea.is_alias_of is not None:
            handle.append(crea.is_alias_of)
        for news in Creator.objects.filter(is_alias_of=crea):
            handle.append(news)
        for name in get_words_in_str(crea.name):
            names.add(name)
        for name in get_words_in_str(crea.given_names):
            names.add(name)
        creators.add(crea)
    return names


# TODO:  This shall go once series also have moved into the new structure.
class AuthorWordMatch(WordMatch):
    creator = models.ForeignKey(Creator, on_delete=CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "AUTHOR"

    @staticmethod
    def get_all_for_author(work: Publication, creator: Creator, words):
        for name in get_all_given_names(creator):
            AuthorWordMatch.objects.create(word=get_word_from_set(name, words), publication=work, creator=creator)

    @staticmethod
    def get_all_for_authors(work: Publication, words=None):
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


# TODO:  This shall go once series also have moved into the new structure.
class SeriesWordMatch(WordMatch):
    series = models.ForeignKey(Series, on_delete=CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "SERIES"

    @staticmethod
    def get_all_for_series(work: Publication, series: Series, words):
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
    def get_all_for_serieses(work: Publication, words=None):
        if words is None:
            words = {}
            for word in SearchWord.objects.all():
                words[word.word] = word
        ser = list(work.workinseries_set.all())
        handled = []
        for series in ser:
            if series in handled:
                continue
            if not series.part_of_series:
                continue
            SeriesWordMatch.get_all_for_series(work, series.part_of_series, words)

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
            for pub in Publication.objects.filter(workinseries__part_of_series_id=s.pk):
                WordMatch.create_all_for(pub, words)
            for ss in Series.objects.filter(part_of_series_id=s.pk):
                serieses.append(ss)

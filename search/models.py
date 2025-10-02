from django.contrib.postgres.indexes import GinIndex
from django.db import models

# Create your models here.
from django.db.models import CASCADE

from book_code_generation.helpers import normalize_str
from creators.models import Creator
from series.models import Series
from works.models import Publication, SubWork


class SearchWord(models.Model):
    word = models.CharField(max_length=255, db_index=True)

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
            for word in SearchWord.objects.all():
                words[word.word] = word

        WordMatch.objects.filter(publication=work).delete()
        for word in get_words_in_str(work.article):
            WordMatch.objects.create(word=get_word_from_set(word, words), publication=work)
        for word in get_words_in_str(work.title):
            WordMatch.objects.create(word=get_word_from_set(word, words), publication=work)
        for word in get_words_in_str(work.sub_title):
            WordMatch.objects.create(word=get_word_from_set(word, words), publication=work)
        for word in get_words_in_str(work.original_article):
            WordMatch.objects.create(word=get_word_from_set(word, words), publication=work)
        for word in get_words_in_str(work.original_title):
            WordMatch.objects.create(word=get_word_from_set(word, words), publication=work)
        for word in get_words_in_str(work.original_subtitle):
            WordMatch.objects.create(word=get_word_from_set(word, words), publication=work)
        AuthorWordMatch.get_all_for_authors(work, words)
        SeriesWordMatch.get_all_for_serieses(work, words)
        SubWorkWordMatch.get_all_for_subworks(work, words)
        return words


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
            for pub in Publication.objects.filter(workinseries__part_of_series_id=s.pk):
                WordMatch.create_all_for(pub, words)
            for ss in Series.objects.filter(part_of_series_id=s.pk):
                serieses.append(ss)


class SubWorkWordMatch(WordMatch):
    sub_work = models.ForeignKey(SubWork, on_delete=CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "SUBWORK"

    @staticmethod
    def get_all_for_subwork(work: Publication, sub_work: SubWork, words):
        for word in get_words_in_str(sub_work.article):
            SubWorkWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, sub_work=sub_work)
        for word in get_words_in_str(sub_work.original_language):
            SubWorkWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, sub_work=sub_work)
        for word in get_words_in_str(sub_work.title):
            SubWorkWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, sub_work=sub_work)
        for word in get_words_in_str(sub_work.sub_title):
            SubWorkWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, sub_work=sub_work)
        for word in get_words_in_str(sub_work.original_title):
            SubWorkWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, sub_work=sub_work)
        for word in get_words_in_str(sub_work.original_subtitle):
            SubWorkWordMatch.objects.create(word=get_word_from_set(word, words), publication=work, sub_work=sub_work)

    @staticmethod
    def get_all_for_subworks(work: Publication, words=None):
        if words is None:
            words = {}
            for word in SearchWord.objects.all():
                words[word.word] = word
        for series in list(work.get_sub_works()):
            SubWorkWordMatch.get_all_for_subwork(work, series.work, words)
            for author in series.get_authors():
                AuthorWordMatch.get_all_for_author(work, author.creator, words)

    @staticmethod
    def subwork_rename(subwork: SubWork):
        SubWorkWordMatch.objects.filter(sub_work=subwork).delete()
        words = {}
        for word in SearchWord.objects.all():
            words[word.word] = word
        for pub in subwork.workinpublication_set.all():
            WordMatch.create_all_for(pub.publication, words)

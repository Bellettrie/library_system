from _testcapi import instancemethod
from typing import List

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView, ListView

from series.models import Series
from utils.get_query_words import get_query_words
from works.models import Work, Publication, Creator, SubWork, CreatorToWork, Item


def sort_works(work: Work):
    return work.old_id


class ItemRow:
    def __init__(self, item: Item, book_result=None, options=[], extra_info = None):
        self.item = item
        self.book_result = book_result
        self.options = options
        self.extra_info = extra_info

    def __str__(self):
        return self.item.signature


class BookResult:
    def __init__(self, publication: Publication, item_rows: List[ItemRow], item_options = [], publication_options = []):
        self.publication = publication
        self.item_rows = item_rows
        self.item_options = item_options
        self.publication_options = publication_options
        for row in self.item_rows:
            row.options = item_options
            row.book_result = self

    def set_item_options(self, item_options):
        for row in self.item_rows:
            row.options = item_options


def get_works(request):
    words = get_query_words(request)
    if words is None or words == []:
        return []

    result_set = None
    for word in words:
        authors = Creator.objects.filter(name__icontains=word)
        series = set(Series.objects.filter(Q(creatortoseries__creator__in=authors) | Q(title__icontains=word)))

        subworks = set(SubWork.objects.filter(
            Q(creatortowork__creator__in=authors) |
            Q(title__icontains=word) |
            Q(workinseries__part_of_series__in=series)))

        word_set = set(Publication.objects.filter(
            Q(creatortowork__creator__in=authors) |
            Q(title__icontains=word) |
            Q(workinseries__part_of_series__in=series) | Q(workinpublication__work__in=subworks)))

        if result_set is None:
            result_set = word_set
        else:
            result_set = result_set & word_set
    l = list(set(result_set))
    l.sort(key=sort_works)
    result = []
    for row in l:
        item_rows = []
        for item in row.item_set.all():
            item_rows.append(ItemRow(item, []))
        result.append(BookResult(row, item_rows))
    return result


class WorkList(ListView):
    model = Work
    template_name = 'work_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        return context

    def get_queryset(self):  # new
        result = get_works(self.request)
        for row in result:
            row.set_item_options(["lend", "reserve"])
            row.publication_options=["edit"]
        return result


class WorkDetail(DetailView):
    template_name = 'work_detail.html'

    model = Publication

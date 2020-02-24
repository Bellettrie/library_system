from _testcapi import instancemethod

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView, ListView

from series.models import Series
from utils.get_query_words import get_query_words
from works.models import Work, Publication, Creator, SubWork, CreatorToWork


def sort_works(work: Work):
    return work.old_id


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
        words = get_query_words(self.request)
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
        return l


class WorkDetail(DetailView):
    template_name = 'work_detail.html'

    model = Publication

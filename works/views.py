from _testcapi import instancemethod

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView, ListView

from series.models import Series
from works.models import Work, Publication, Creator, SubWork


class WorkList(ListView):
    model = Work
    template_name = 'work_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['book_list'] = Work.objects.all()
        return context

    def get_queryset(self):  # new

        query = self.request.GET.get('q')
        if query is None:
            return []
        words = query.split(" ")
        if len(words) == 0:
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

        return list(set(result_set))


class WorkDetail(DetailView):
    template_name = 'work_detail.html'

    model = Publication

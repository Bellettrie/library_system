from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView, ListView

from series.models import Series
from works.models import Work, Publication, Creator


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
        words = query.split(" ")
        query = None
        author_query = None
        for word in words:
            nq = Q(title__icontains=word)
            aq = Q(name__icontains=word)

            if query is None:
                query = nq
                author_query = aq
            else:
                query = query & nq
                author_query = author_query & aq

        authors = Creator.objects.filter(author_query)
        series_list = Series.objects.filter(query)

        series_set = set(series_list) | set(Series.objects.filter(creatortoseries__creator__in=authors))
        ssize = 0
        while len(series_set) > ssize:
            ssize = len(series_set)
            series_set = series_set | set(Series.objects.filter(part_of_series__in=series_set))

        object_list = Work.objects.filter(
            query | Q(creatortowork__creator__in=authors) | Q(workinseries__part_of_series__in=series_set)
        )
        return list(set(object_list))


class WorkDetail(DetailView):
    template_name = 'work_detail.html'

    model = Publication

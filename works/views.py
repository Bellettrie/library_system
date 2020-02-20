from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView, ListView

from works.models import Work, Publication


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
        object_list = Work.objects.filter(
            Q(title__contains=query)
        )
        return object_list


class WorkDetail(DetailView):
    template_name = 'work_detail.html'

    model = Publication

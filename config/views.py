from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django_tables2 import LazyPaginator

from config.models import Holiday


class HolidayList(ListView):
    template_name = 'holiday_list.html'
    model = Holiday
    pagination_class = LazyPaginator

    def get_queryset(self):  # new
        return Holiday.objects.all().order_by('-ending_date')


class HolidayCreate(CreateView):
    model = Holiday
    fields = ['name', 'starting_date', 'ending_date']
    template_name = 'holiday_form.html'


class HolidayUpdate(UpdateView):
    model = Holiday
    fields = ['name', 'starting_date', 'ending_date']
    template_name = 'holiday_form.html'


class HolidayDelete(DeleteView):
    model = Holiday
    template_name = 'holiday_confirm_delete.html'
    success_url = reverse_lazy('holiday.view')


class HolidayDetail(DetailView):
    template_name = 'holiday_detail.html'
    model = Holiday

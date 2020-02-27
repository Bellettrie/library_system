from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView

from config.models import Holiday


class HolidayList(ListView):
    template_name = 'holiday_list.html'
    model = Holiday


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
    success_url = reverse_lazy('holiday-list')


class HolidayDetail(DetailView):
    template_name = 'holiday_detail.html'
    model = Holiday

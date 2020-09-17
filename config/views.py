from django.contrib.auth.mixins import PermissionRequiredMixin

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django_tables2 import LazyPaginator

from django import forms
from config.models import Holiday


class HolidayList(PermissionRequiredMixin, ListView):
    permission_required = 'config.view_holiday'
    template_name = 'holiday_list.html'
    model = Holiday
    pagination_class = LazyPaginator

    def get_queryset(self):  # new
        return Holiday.objects.all().order_by('-ending_date')


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'starting_date', 'ending_date']
        widgets = {
            'starting_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'ending_date': forms.DateInput(attrs={'class': 'datepicker'})
        }


class HolidayCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'config.add_holiday'
    model = Holiday
    form_class = HolidayForm
    template_name = 'holiday_form.html'


class HolidayUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'config.change_holiday'
    model = Holiday
    form_class = HolidayForm
    template_name = 'holiday_form.html'


class HolidayDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'config.delete_holiday'
    model = Holiday
    template_name = 'holiday_confirm_delete.html'
    success_url = reverse_lazy('holiday.view')


class HolidayDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'config.view_holiday'
    template_name = 'holiday_detail.html'
    model = Holiday

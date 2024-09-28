from django.urls import path

from utils.wrappers import hx_wrap
from .views import get_series_by_query, view_series, edit_series, new_series, delete_series, SeriesList, new_codegen, \
    location_code_set_form, location_code_set_gen, location_code_delete_form

urlpatterns = [
    path('search/<search_text>', get_series_by_query, name='series.query'),
    path('views/<slug:pk>', view_series, name='series.views'),
    path('edit/<slug:pk>', edit_series, name='series.edit'),
    path('delete/<slug:pk>', delete_series, name='series.delete'),
    path('list', SeriesList.as_view(), name='series.list'),

    path('new', new_series, name='series.new'),

    path('code-gen/<slug:pk>', new_codegen, name='series.gen_code'),
    path('code-gen/hx/<slug:pk>', hx_wrap(new_codegen), name='series.gen_code_hx'),

    path('code-gen/cutter-delete/<slug:pk>', location_code_delete_form, name='series.cutter.del_code'),
    path('code-gen/cutter-delete/hx/<slug:pk>', hx_wrap(location_code_delete_form), name='series.cutter.del_code_hx'),

    path('code-gen/cutter/<slug:pk>', location_code_set_form, name='series.cutter.gen_code'),
    path('code-gen/cutter/hx/<slug:pk>', hx_wrap(location_code_set_form), name='series.cutter.gen_code_hx'),
    path('code-gen/cutter/<slug:pk>/generate', location_code_set_gen, name='series.cutter.gen_code_hx_gen'),
]

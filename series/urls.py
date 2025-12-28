from django.urls import path

from utils.wrappers import hx_wrap
from .views import get_series_by_query, edit_series, new_series, delete_series, SeriesList, new_codegen, \
    location_code_set_form, location_code_set_gen, location_code_delete_form

urlpatterns = [
    path('search/<search_text>', get_series_by_query, name='series.query'),

    path('new', new_series, name='series.new'),
    path('list', SeriesList.as_view(), name='series.list'),
    path('<slug:pk>edit', edit_series, name='series.edit'),
    path('<slug:pk>/delete', delete_series, name='series.delete'),


    path('<slug:series_id>/book-code/set', hx_wrap(new_codegen), name='series.book_code.set'),
    path('<slug:series_id>/location-book-code/delete', hx_wrap(location_code_delete_form), name='series.location_book_code.delete'),
    path('<slug:series_id>/location-book-code/set', hx_wrap(location_code_set_form), name='series.location_book_code.set'),
    path('<slug:series_id>/location-book-code/generate', location_code_set_gen, name='series.location_book_code.generate'),
]

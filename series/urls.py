from django.urls import path

from .views import get_series_by_query, view_series, edit_series, new_series, delete_series, SeriesList

urlpatterns = [
    path('search/<search_text>', get_series_by_query, name='series.query'),
    path('view/<slug:pk>', view_series, name='series.view'),
    path('edit/<slug:pk>', edit_series, name='series.edit'),
    path('delete/<slug:pk>', delete_series, name='series.delete'),
    path('list', SeriesList.as_view(), name='series.list'),

    path('new', new_series, name='series.new'),
]

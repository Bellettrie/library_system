from django.urls import path

from . import views
from .views import print_list


def a():
    pass


urlpatterns = [
    path('', a, name='inventarisation.list'),
    path('new', a, name='inventarisation.new'),
    path('printList/<slug:inventarisation_id>', print_list, name='inventarisation.print'),
    path('list/<slug:inventarisation_id>/<slug:page_id>', a, name='inventarisation.by_number'),
    path('list/<slug:inventarisation_id>/next', a, name='inventarisation.next')
]

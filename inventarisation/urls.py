from django.urls import path

from . import views
from .views import print_list, list_inventarisations, InventarisationCreate, get_inventarisation_next, inventarisation_form


def a():
    pass


urlpatterns = [
    path('', list_inventarisations, name='inventarisation.list'),
    path('new', InventarisationCreate.as_view(), name='inventarisation.new'),
    path('printList/<slug:inventarisation_id>', print_list, name='inventarisation.print'),
    path('list/<slug:inventarisation_id>/<slug:page_id>', inventarisation_form, name='inventarisation.by_number'),
    path('list/<slug:inventarisation_id>/<slug:page_id>/next', get_inventarisation_next, name='inventarisation.next')
]

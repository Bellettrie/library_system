from django.urls import path

from . import views
from .views import print_list, list_inventarisations, InventarisationCreate, get_inventarisation_next, inventarisation_form, get_inventarisation_finish, get_inventarisation_finished, \
    get_inventarisation_early_end, get_inventarisation_for_all


def a():
    pass


urlpatterns = [
    path('', list_inventarisations, name='inventarisation.list'),
    path('new', InventarisationCreate.as_view(), name='inventarisation.new'),
    path('printList/<slug:inventarisation_id>', print_list, name='inventarisation.print'),
    path('list/<slug:inventarisation_id>/<slug:page_id>', inventarisation_form, name='inventarisation.by_number'),
    path('list/<slug:inventarisation_id>/<slug:page_id>/next', get_inventarisation_next, name='inventarisation.next'),
    path('for-all', get_inventarisation_for_all, name='inventarisation.forAll'),
    path('finish/<slug:inventarisation_id>', get_inventarisation_finish, name='inventarisation.finish'),
    path('finished/<slug:inventarisation_id>', get_inventarisation_finished, name='inventarisation.finished'),
    path('early/<slug:inventarisation_id>', get_inventarisation_early_end, name='inventarisation.early')
]

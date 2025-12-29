from django.urls import path

from . import views
from .views import print_list, list_inventarisations, InventarisationCreate, get_inventarisation_next, \
    inventarisation_form, get_inventarisation_finish, get_inventarisation_finished, \
    get_inventarisation_early_end, get_inventarisation_for_all


urlpatterns = [
    path('', list_inventarisations, name='inventarisations.inventarisation.list'),
    path('new', InventarisationCreate.as_view(), name='inventarisations.inventarisation.new'),
    path('new/for-all', get_inventarisation_for_all, name='inventarisations.inventarisation.forAll'),

    path('printList/<slug:inventarisation_id>', print_list, name='inventarisations.inventarisation.print'),
    path('<slug:inventarisation_id>/page/<slug:page_id>', inventarisation_form,
         name='inventarisations.inventarisation.by_number'),
    path('<slug:inventarisation_id>/page/<slug:page_id>/next', get_inventarisation_next,
         name='inventarisations.inventarisation.next'),

    path('<slug:inventarisation_id>/finish', get_inventarisation_finish,
         name='inventarisations.inventarisation.finish'),
    path('<slug:inventarisation_id>/finished', get_inventarisation_finished,
         name='inventarisations.inventarisation.finished'),
    path('<slug:inventarisation_id>/finish/early', get_inventarisation_early_end,
         name='inventarisations.inventarisation.early')
]

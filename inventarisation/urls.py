from django.urls import path

from .views import print_list, list_inventarisations, InventarisationCreate, get_inventarisation_next, \
    inventarisation_form, get_inventarisation_finish, get_inventarisation_finished, \
    get_inventarisation_early_end, get_inventarisation_for_all

urlpatterns = [
    path('', list_inventarisations, name='inventarisations.list'),
    path('new', InventarisationCreate.as_view(), name='inventarisations.new'),
    path('new/for-all', get_inventarisation_for_all, name='inventarisations.forAll'),

    path('<slug:inventarisation_id>/print', print_list, name='inventarisations.print'),
    path('<slug:inventarisation_id>/page/<slug:page_id>', inventarisation_form, name='inventarisations.page'),
    path('<slug:inventarisation_id>/page/<slug:page_id>/next', get_inventarisation_next,
         name='inventarisations.page.next'),

    path('<slug:inventarisation_id>/finish', get_inventarisation_finish, name='inventarisations.finish'),
    path('<slug:inventarisation_id>/finished', get_inventarisation_finished, name='inventarisations.finished'),
    path('<slug:inventarisation_id>/finish/early', get_inventarisation_early_end, name='inventarisations.finish.early')
]

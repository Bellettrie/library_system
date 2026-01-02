from django.urls import path

from utils.wrappers import hx_wrap

from .views.delete_reservation import delete_reservation
from .views.finalize_reservation_based import finalize_reservation_based
from .views.reserve_finalize import reserve_finalize
from .views.reserve_item import reserve_item
from .views.reserve_list import reserve_list

urlpatterns = [
    path('list', reserve_list, name='reservations.list'),
    path('item/<int:item_id>/reserve', reserve_item, name='reservations.item'),
    path('item/<int:work_id>/member/<int:member_id>/finalize', hx_wrap(reserve_finalize), name='reservations.finalize'),
    path('<slug:reservation_id>/lendfor', hx_wrap(finalize_reservation_based), name='reservations.lendfor'),
    path('<slug:reservation_id>/delete/', hx_wrap(delete_reservation), name='reservations.delete'),
]

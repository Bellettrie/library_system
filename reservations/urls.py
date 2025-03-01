from django.urls import path

from utils.wrappers import hx_wrap

from .views.delete_reservation import delete_reservation
from .views.finalize_reservation_based import finalize_reservation_based
from .views.reserve_failed import reserve_failed
from .views.reserve_finalize import reserve_finalize
from .views.reserve_item import reserve_item
from .views.reserve_list import reserve_list

urlpatterns = [
    path('list', reserve_list, name='reservations.list'),
    path('reserve/item/<int:item_id>', reserve_item, name='reservations.item'),
    path('reserve/finalize/<int:work_id>/<int:member_id>', reserve_finalize, name='reservations.finalize'),
    path('reserve/failed/<int:work_id>/<int:member_id>/<int:reason_id>', reserve_failed, name='reservations.finalize.failed'),
    path('reserve/lendfor/<slug:reservation_id>', hx_wrap(finalize_reservation_based), name='reservations.lendfor'),
    path('reserve/delete/<slug:reservation_id>', hx_wrap(delete_reservation), name='reservations.delete'),

]

from django.urls import path

from utils.wrappers import hx_wrap
from .path_names import RESERVE_LIST, RESERVE_ITEM, RESERVE_MEMBER, RESERVE_FINALIZE, RESERVE_FAILED, RESERVE_LEND

from .views.delete_reservation import delete_reservation
from .views.finalize_reservation_based import finalize_reservation_based
from .views.reserve_failed import reserve_failed
from .views.reserve_finalize import reserve_finalize
from .views.reserve_member import reserve_member
from .views.reserve_item import reserve_item
from .views.reserve_list import reserve_list

urlpatterns = [
    path('list', reserve_list, name=RESERVE_LIST),
    path('reserve/item/<int:item_id>', reserve_item, name=RESERVE_ITEM),
    path('reserve/member/<int:member_id>', reserve_member, name=RESERVE_MEMBER),
    path('reserve/finalize/<int:work_id>/<int:member_id>', reserve_finalize, name=RESERVE_FINALIZE),
    path('reserve/failed/<int:work_id>/<int:member_id>/<int:reason_id>', reserve_failed, name=RESERVE_FAILED),
    path('reserve/lendfor/<slug:reservation_id>', hx_wrap(finalize_reservation_based), name=RESERVE_LEND),
    path('reserve/delete/<slug:reservation_id>', hx_wrap(delete_reservation), name='lendings.reserve_delete'),

]

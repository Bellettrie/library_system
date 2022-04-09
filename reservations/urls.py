from django.urls import path

from .path_names import RESERVE_LIST, RESERVE_ITEM, RESERVE_MEMBER, RESERVE_FINALIZE, RESERVE_FAILED, RESERVE_LEND, RESERVE_DELETE

from .views.delete_reservation import delete_reservation
from .views.finalize_reservation_based import finalize_reservation_based
from .views.reserve_failed import reserve_failed
from .views.reserve_finalize import reserve_finalize
from .views.reserve_member import reserve_member
from .views.reserve_item import reserve_item
from .views.reserve_list import reserve_list

urlpatterns = [
    path('list', reserve_list, name=RESERVE_LIST),
    path('reserve_item/<int:item_id>', reserve_item, name=RESERVE_ITEM),
    path('reserve_member/<int:member_id>', reserve_member, name=RESERVE_MEMBER),
    path('reserve_finalize/<int:work_id>/<int:member_id>', reserve_finalize, name=RESERVE_FINALIZE),
    path('failed_reservation/<int:work_id>/<int:member_id>/<int:reason_id>', reserve_failed, name=RESERVE_FAILED),
    path('finalize_reservation_based/<slug:reservation_id>', finalize_reservation_based, name=RESERVE_LEND),
    path('delete_reservation/<slug:reservation_id>', delete_reservation, name=RESERVE_DELETE),

]

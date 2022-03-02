from django.urls import path

from reservations.path_names import RESERVE_LIST, RESERVE_ITEM, RESERVE_MEMBER, RESERVE_FINALIZE, RESERVE_FAILED, RESERVE_LEND, RESERVE_DELETE

from .views.index import index
from .views.extend import extend
from .views.finalize import finalize
from .views.item_based import item_based
from .views.lending_failed import lending_failed
from .views.member_based import member_based
from .views.reservation import return_book, me, reserve_list, reserve_item, reserve_member, reserve_finalize, reserve_failed, finalize_reservation_based, delete_reservation

urlpatterns = [
    path('list', reserve_list, name=RESERVE_LIST),
    path('reserve_item/<int:work_id>', reserve_item, name=RESERVE_ITEM),
    path('reserve_member/<int:member_id>', reserve_member, name=RESERVE_MEMBER),
    path('reserve_finalize/<int:work_id>/<int:member_id>', reserve_finalize, name=RESERVE_FINALIZE),
    path('failed_reservation/<int:work_id>/<int:member_id>/<int:reason_id>', reserve_failed, name=RESERVE_FAILED),
    path('finalize_reservation_based/<slug:id>', finalize_reservation_based, name=RESERVE_LEND),
    path('delete_reservation/<slug:id>', delete_reservation, name=RESERVE_DELETE),

]

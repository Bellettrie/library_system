from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND, LENDING_FAILED, LENDING_HISTORY

from .views.extend import extend, hx_extend
from .views.finalize import finalize
from .views.item_based import item_based
from .views.lending_failed import lending_failed
from .views.lending_history import LendingHistory
from .views.lendings_list import LendingList
from .views.me import lendings_and_reservations
from .views.member_based import member_based
from .views.register_returned import return_item

urlpatterns = [
    path('', LendingList.as_view(), name=LENDING_LIST),
    path('work/<int:work_id>', item_based, name=LENDING_NEW_WORK),
    path('member/<int:member_id>', member_based, name=LENDING_NEW_MEMBER),
    path('finalize/<int:work_id>/<int:member_id>', finalize, name=LENDING_FINALIZE),
    path('failed_lending/<int:work_id>/<int:member_id>/<int:reason_id>', lending_failed, name=LENDING_FAILED),
    path('extend/<int:work_id>', extend, name=LENDING_EXTEND),
    path('extend/hx/<int:work_id>', hx_extend, name=LENDING_EXTEND+"_hx"),
    path('return/<int:work_id>', return_item, name=LENDING_RETURNBOOK),
    path('me/', lendings_and_reservations, name=LENDING_MY_LENDINGS),
    path('history/<int:work_id>', LendingHistory.as_view(), name=LENDING_HISTORY),
]

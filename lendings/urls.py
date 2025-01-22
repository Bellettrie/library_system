from django.urls import path

from utils.wrappers import hx_wrap

from .views.extend import extend
from .views.finalize import finalize

from .views.item_based import item_based
from .views.lending_history import LendingHistory
from .views.lendings_list import LendingList
from .views.me import lendings_and_reservations
from .views.member_based import member_based
from .views.register_returned import return_item

urlpatterns = [
    path('', LendingList.as_view(), name='lendings.list'),
    path('new_from_work/<int:work_id>', item_based, name='lendings.new.work'),
    path('new_from_member/<int:member_id>', member_based, name='lendings.new.member'),
    path('finalize/<int:work_id>/<int:member_id>', hx_wrap(finalize), name='lendings.finalize'),
    path('extend/<int:work_id>', hx_wrap(extend), name='lendings.extend'),
    path('return/<int:work_id>', hx_wrap(return_item), name='lendings.returnbook'),
    path('me/', lendings_and_reservations, name='lendings.me'),
    path('history/<int:work_id>', LendingHistory.as_view(), name='lendings.history'),
]

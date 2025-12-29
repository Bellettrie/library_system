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

    path('member/<int:member_id>', member_based, name='lendings.for_member.new'),
    path('item/<int:item_id>/new', item_based, name='lendings.for_item.new'),
    path('item/<int:item_id>/member/<int:member_id>', hx_wrap(finalize), name='lendings.item.finalize'),
    path('item/<int:item_id>/extend/', hx_wrap(extend), name='lendings.item.extend'),
    path('item/<int:item_id>/return/', hx_wrap(return_item), name='lendings.item.return'),
    path('item/<int:item_id>/history/', LendingHistory.as_view(), name='lendings.item.history'),

    path('me/', lendings_and_reservations, name='lendings.member.view'),
]

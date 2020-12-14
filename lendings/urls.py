from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND, LENDING_FAILED, \
    RESERVE_LIST, RESERVE_ITEM, RESERVE_MEMBER, RESERVE_FINALIZE, RESERVE_FAILED

from . import views
from .views import index

urlpatterns = [
    path('', index, name=LENDING_LIST),
    path('work/<int:work_id>', views.work_based, name=LENDING_NEW_WORK),
    path('member/<int:member_id>', views.member_based, name=LENDING_NEW_MEMBER),
    path('finalize/<int:work_id>/<int:member_id>', views.finalize, name=LENDING_FINALIZE),
    path('failed_lending/<int:work_id>/<int:member_id>/<int:reason_id>', views.lending_failed, name=LENDING_FAILED),
    path('extend/<int:work_id>', views.extend, name=LENDING_EXTEND),
    path('return/<int:work_id>', views.return_book, name=LENDING_RETURNBOOK),
    path('me/', views.me, name=LENDING_MY_LENDINGS),
    path('reservations', views.reserve_list, name=RESERVE_LIST),
    path('reserve_work/<int:work_id>', views.reserve_item, name=RESERVE_ITEM),
    path('reserve_member/<int:member_id>', views.reserve_member, name=RESERVE_MEMBER),
    path('reserve_finalize/<int:work_id>/<int:member_id>', views.reserve_finalize, name=RESERVE_FINALIZE),
    path('failed_reservation/<int:work_id>/<int:member_id>/<int:reason_id>', views.reserve_failed, name=RESERVE_FAILED),
]

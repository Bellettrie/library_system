from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND, LENDING_FAILED

from .views.index import index
from .views.extend import extend
from .views.finalize import finalize
from .views.item_based import item_based
from .views.lending_failed import lending_failed
from .views.me import me
from .views.member_based import member_based
from .views.register_returned import register_returned

urlpatterns = [
    path('', index, name=LENDING_LIST),
    path('work/<int:work_id>', item_based, name=LENDING_NEW_WORK),
    path('member/<int:member_id>', member_based, name=LENDING_NEW_MEMBER),
    path('finalize/<int:work_id>/<int:member_id>', finalize, name=LENDING_FINALIZE),
    path('failed_lending/<int:work_id>/<int:member_id>/<int:reason_id>', lending_failed, name=LENDING_FAILED),
    path('extend/<int:work_id>', extend, name=LENDING_EXTEND),
    path('return/<int:work_id>', register_returned, name=LENDING_RETURNBOOK),
    path('me/', me, name=LENDING_MY_LENDINGS),
]

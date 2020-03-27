from django.urls import path

from bellettrie_library_system.permissions import simple_path, PERM_ALL
from lendings.permissions import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER

from members.views import MemberList
from . import views
from .views import index

urlpatterns = [
    path('', index, name=LENDING_LIST),
    path('work/<int:work_id>', views.work_based, name=LENDING_NEW_WORK),
    path('member/<int:member_id>', views.member_based, name=LENDING_NEW_MEMBER),
    path('finalize/<int:work_id>/<int:member_id>', views.finalize, name=LENDING_FINALIZE),
    path('me/', views.me, name=LENDING_MY_LENDINGS),

]

from django.urls import path

from bellettrie_library_system.permissions import authorized_path, PERM_ALL
from lendings.permissions import LENDING_VIEW, LENDING_LIST, LENDING_NEW, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS

from members.views import MemberList
from . import views

urlpatterns = [
    authorized_path('', MemberList.as_view(), LENDING_LIST),
    authorized_path('work/<int:work_id>', views.work_based, LENDING_VIEW),
    authorized_path('work/<int:work_id>', views.work_based, LENDING_NEW),
    authorized_path('finalize/<int:work_id>/<int:member_id>', views.finalize, LENDING_NEW, name=LENDING_FINALIZE),
    authorized_path('me/', views.me, PERM_ALL, name=LENDING_MY_LENDINGS),

]

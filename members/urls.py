from bellettrie_library_system.permissions import authorize, authorized_path
from django.urls import path

from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT
from members.views import MemberList
from . import views

urlpatterns = [
    path('', MemberList.as_view(), name=MEMBERS_LIST),
    path('<int:member_id>', views.show, name=MEMBERS_VIEW),
    path('<int:member_id>/edit', views.edit, name=MEMBERS_EDIT),
    path('new', views.new, name=MEMBERS_NEW),

]
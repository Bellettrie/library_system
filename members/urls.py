from bellettrie_library_system.permissions import authorize, authorized_path
from django.urls import path

from members.permissions import MEMBERS_LIST
from members.views import MemberList
from . import views

urlpatterns = [
    authorized_path('', MemberList.as_view(), MEMBERS_LIST),

    path('', MemberList.as_view(), name='members-list'),
    path('<int:member_id>', views.show, name='show_member'),
    path('<int:member_id>/edit', views.edit, name='edit_member'),
    path('new', views.new, name='new_member'),

]
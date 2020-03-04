from members.permissions import authorize, permits, VIEW
from django.urls import path

from members.views import MemberList
from . import views

urlpatterns = [
    path('', authorize(VIEW, permits)(MemberList.as_view()), name='members-list'),
    path('<int:member_id>', views.show, name='show_member'),
    path('<int:member_id>/edit', views.edit, name='edit_member'),
    path('new', views.new, name='new_member'),

]
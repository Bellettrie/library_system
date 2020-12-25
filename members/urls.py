from django.urls import path

from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT, MEMBERS_DELETE
from members.views import MemberList, signup, delete_user, change_user, remove_user, edit_membership_period, new_membership_period, AnonMemberList
from . import views

urlpatterns = [
    path('', MemberList.as_view(), name=MEMBERS_LIST),
    path('anon', AnonMemberList.as_view(), name='members.list.anon'),

    path('<int:member_id>', views.show, name=MEMBERS_VIEW),
    path('<int:member_id>/edit', views.edit, name=MEMBERS_EDIT),
    path('<int:member_id>/invite', views.generate_invite_code, name='members.generate_invite'),
    path('<int:member_id>/uninvite', views.disable_invite_code, name='members.disable_invite'),
    path('<int:member_id>/delete', views.delete_member, name='members.delete'),
    path('<int:member_id>/anonymise', views.anonymise, name='members.anonymise'),

    path('new', views.new, name=MEMBERS_NEW),
    path('signup/<int:member_id>', signup, name='members.signup'),
    path('change_user/<int:member_id>', change_user, name='members.change_user'),
    path('remove_user/<int:member_id>', remove_user, name='members.remove_user'),
    path('del_user/<int:member_id>', delete_user, name='members.delete_user'),

    path('edit_membership_period/<int:membership_period_id>', edit_membership_period, name='members.membership_period_edit'),
    path('new_membership_period/<int:member_id>', new_membership_period, name='members.membership_period_new'),
]

from django.urls import path

import members.views.anonymise
import members.views.anonymise_list
import members.views.user.invite_code_disable
import members.views.user.invite_code_generate
import members.views.member_delete
import members.views.member_edit
import members.views.member_new
import members.views.member_show
from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT, MEMBERS_DELETE
from .views.member_list import MemberList
from .views.anon_member_list import AnonMemberList
from .views.user.signup import signup
from members.views.user.edit import change_user
from .views.user.delete import delete_user, delete_user_prompt
from .views.membership_period_edit import edit_membership_period
from .views.membership_period_new import new_membership_period

urlpatterns = [
    path('', MemberList.as_view(), name=MEMBERS_LIST),
    path('anon', AnonMemberList.as_view(), name='members.list.anon'),

    path('<int:member_id>', members.views.member_show.show, name=MEMBERS_VIEW),
    path('<int:member_id>/edit', members.views.member_edit.edit, name=MEMBERS_EDIT),
    path('<int:member_id>/invite', members.views.user.invite_code_generate.generate_invite_code, name='members.generate_invite'),
    path('<int:member_id>/uninvite', members.views.user.invite_code_disable.disable_invite_code, name='members.disable_invite'),
    path('<int:member_id>/delete', members.views.member_delete.delete_member, name='members.delete'),
    path('<int:member_id>/anonymise', members.views.anonymise.anonymise, name='members.anonymise'),
    path('anonymise_list', members.views.anonymise_list.anonymise_list, name='members.anonymise_all'),

    path('new', members.views.member_new.new, name=MEMBERS_NEW),
    path('signup/<int:member_id>', members.views.user.signup.signup, name='members.signup'),
    path('change_user/<int:member_id>', members.views.user.edit.change_user, name='members.change_user'),
    path('remove_user/<int:member_id>', members.views.user.delete.delete_user_prompt, name='members.remove_user'),
    path('del_user/<int:member_id>', members.views.user.delete.delete_user, name='members.delete_user'),

    path('edit_membership_period/<int:membership_period_id>', members.views.membership_period_edit.edit_membership_period, name='members.membership_period_edit'),
    path('new_membership_period/<int:member_id>', members.views.membership_period_new.new_membership_period, name='members.membership_period_new'),
]

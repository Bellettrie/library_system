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
from utils.wrappers import hx_wrap
from .views.committees import join_committee, leave_committee
from .views.member_list import MemberList
from .views.anon_member_list import AnonMemberList
from .views.user.self_signup import self_signup
from .views.user.signup import signup
from members.views.user.edit import change_own_password
from .views.user.delete import delete_user
from .views.membership_period_edit import edit_membership_period
from .views.membership_period_new import new_membership_period
from .views.auth.by_committee import webcie

urlpatterns = [
    path('', MemberList.as_view(), name=MEMBERS_LIST),
    path('anon', AnonMemberList.as_view(), name='members.list.anon'),
    path('anonymise/<int:member_id>', members.views.anonymise.anonymise, name='members.anonymise'),
    path('anonymise/list', members.views.anonymise_list.anonymise_list, name='members.anonymise_all'),
    path('new', members.views.member_new.new, name=MEMBERS_NEW),

    path('<int:member_id>/<int:full>', members.views.member_show.show, name=MEMBERS_VIEW),
    path('<int:member_id>/edit', members.views.member_edit.edit, name=MEMBERS_EDIT),
    path('<int:member_id>/delete', members.views.member_delete.delete_member, name='members.delete'),

    path('<int:member_id>/signup', members.views.user.signup.signup, name='members.signup'),
    # Backwards compabitility with email links we already sent out.
    path('signup/<int:member_id>', members.views.user.signup.signup, name='members.signup_old'),
    path('self/user/password_change', hx_wrap(members.views.user.edit.change_own_password), name='members.change_self'),

    path('user/self-service', self_signup, name='members.self_signup'),

    path('<int:member_id>/invite', members.views.user.invite_code_generate.generate_invite_code,
         name='members.generate_invite'),
    path('<int:member_id>/uninvite', members.views.user.invite_code_disable.disable_invite_code,
         name='members.disable_invite'),
    path('<int:member_id>/user/edit/', hx_wrap(members.views.user.edit.change_user), name='members.change_user'),

    path('<int:member_id>/user/delete', hx_wrap(members.views.user.delete.delete_user),
         name='members.delete_user'),

    path('<int:member_id>/membership_period/new/', hx_wrap(members.views.membership_period_new.new_membership_period),
         name='members.membership_period_new'),
    path('membership_period/<int:membership_period_id>/edit',
         hx_wrap(members.views.membership_period_edit.edit_membership_period), name='members.membership_period_edit'),

    path('<int:member_id>/committee/join/', hx_wrap(join_committee),
         name='members.committee.join'),
    path('<int:member_id>/committee/<int:committee_id>/leave/', hx_wrap(leave_committee),
         name='members.committee.leave'),
    path('auth/by_committee/webcie', members.views.auth.by_committee.webcie, name='members.auth.by_committee.webcie'),

]

from django.urls import path

from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT
from members.views import MemberList, signup, delete_user, change_user, remove_user, edit_membership_period
from . import views

urlpatterns = [
    path('', MemberList.as_view(), name=MEMBERS_LIST),
    path('<int:member_id>', views.show, name=MEMBERS_VIEW),
    path('<int:member_id>/edit', views.edit, name=MEMBERS_EDIT),
    path('<int:member_id>/invite', views.generate_invite_code, name='members.generate_invite'),
    path('<int:member_id>/uninvite', views.disable_invite_code, name='members.disable_invite'),
    path('new', views.new, name=MEMBERS_NEW),
    path('signup/<int:member_id>', signup, name='members.signup'),
    path('change_user/<int:member_id>', change_user, name='members.change_user'),
    path('remove_user/<int:member_id>', remove_user, name='members.remove_user'),
    path('del_user/<int:member_id>', delete_user, name='members.delete_user'),

    path('edit_membership_period/<int:membership_period_id>', edit_membership_period, name='members.membership_period_edit'),

]

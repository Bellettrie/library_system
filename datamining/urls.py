from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND, LENDING_FAILED

from .views import show_mail_addresses, show_members

urlpatterns = [
    path('member_filtered', show_members, name='datamining.members'),
    path('mail_addresses', show_mail_addresses, name='datamining.members_mails'),
]

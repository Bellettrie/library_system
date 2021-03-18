from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND, LENDING_FAILED

from .views import show_members, show_membership_stats, show_lending_stats

urlpatterns = [
    path('member_filtered', show_members, name='datamining.members'),
    path('member_stats', show_membership_stats, name='datamining.membership_stats')
    path('lending_stats', show_lending_stats, name='datamining.lending_stats')
]

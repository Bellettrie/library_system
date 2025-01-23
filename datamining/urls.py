from django.urls import path

from .views import show_members_by_date, show_members_by_group, show_members_by_special
from .views import show_membership_stats, show_lending_stats

urlpatterns = [
    path('member_filtered/date_based', show_members_by_date, name='datamining.members.date_based'),
    path('member_filtered/special', show_members_by_special, name='datamining.members.special'),
    path('member_filtered/groups', show_members_by_group, name='datamining.members.groups'),
    path('member_filtered', show_members_by_date, name='datamining.members'),

    path('member_stats', show_membership_stats, name='datamining.membership_stats'),
    path('lending_stats', show_lending_stats, name='datamining.lending_stats')
]

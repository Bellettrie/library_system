from django.urls import path

from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT
from members.views import MemberList, signup, delete_user, change_user, remove_user
from . import views
from .views import get_series_by_query, view_series, edit_series, new_series

urlpatterns = [
    path('search/<search_text>', get_series_by_query, name='series.query'),
    path('view/<slug:pk>', view_series, name='series.view'),
    path('edit/<slug:pk>', edit_series, name='series.edit'),
    path('new', new_series, name='series.new'),
]

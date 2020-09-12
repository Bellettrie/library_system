from django.urls import path

from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT
from members.views import MemberList, signup, delete_user, change_user, remove_user
from . import views


urlpatterns = [
    path('list', views.RecodeList.as_view(), name='recode.list'),
    path('end/<slug:pk>', views.end_recode, name='recode.end'),

]

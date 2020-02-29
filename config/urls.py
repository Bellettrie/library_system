from django.urls import path

from config.views import HolidayDelete, HolidayUpdate, HolidayCreate, HolidayList, HolidayDetail
from members.views import MemberList
from . import views

urlpatterns = [
    path('holiday/', HolidayList.as_view(), name='holiday-list'),

    path('holiday/add/', HolidayCreate.as_view(), name='holiday-add'),
    path('holiday/<int:pk>/', HolidayDetail.as_view(), name='holiday-view'),
    path('holiday/<int:pk>/edit/', HolidayUpdate.as_view(), name='holiday-update'),

    path('holiday/<int:pk>/delete/', HolidayDelete.as_view(), name='holiday-delete'),
]
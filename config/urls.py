from django.urls import path

from config.views import HolidayDelete, HolidayUpdate, HolidayCreate, HolidayList, HolidayDetail

urlpatterns = [
    path('holiday/list/', HolidayList.as_view(), name='config.holiday.list'),

    path('holiday/<int:pk>/', HolidayDetail.as_view(), name='config.holiday.view'),
    path('holiday/new/', HolidayCreate.as_view(), name='config.holiday.new'),
    path('holiday/<int:pk>/edit/', HolidayUpdate.as_view(), name='config.holiday.edit'),

    path('holiday/<int:pk>/delete/', HolidayDelete.as_view(), name='config.holiday.delete'),
]

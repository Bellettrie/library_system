from django.urls import path

from config.views import HolidayDelete, HolidayUpdate, HolidayCreate, HolidayList, HolidayDetail

urlpatterns = [
    path('holiday/list/', HolidayList.as_view(), name='holiday.list'),

    path('holiday/<int:pk>/', HolidayDetail.as_view(), name='holiday.view'),
    path('holiday/new/', HolidayCreate.as_view(), name='holiday.add'),
    path('holiday/edit/<int:pk>/', HolidayUpdate.as_view(), name='holiday.edit'),

    path('holiday/delete/<int:pk>', HolidayDelete.as_view(), name='holiday.delete'),
]

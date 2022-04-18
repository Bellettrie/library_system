from django.urls import path

from . import views


urlpatterns = [
    path('list', views.RecodeList.as_view(), name='recode.list'),
    path('end/<slug:pk>', views.end_recode, name='recode.end'),

]

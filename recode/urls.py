from django.urls import path

from utils.wrappers import hx_wrap
from . import views


urlpatterns = [
    path('list', views.RecodeList.as_view(), name='recode.list'),
    path('finish/<slug:pk>', hx_wrap(views.recode_finish), name='recode.finish'),
]

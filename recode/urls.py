from django.urls import path

from utils.wrappers import hx_wrap
from . import views


urlpatterns = [
    path('list', views.RecodeList.as_view(), name='recode.list'),
    path('<slug:item_id>/edit', hx_wrap(views.recode_edit), name='recode.edit'),
    path('<slug:pk>/finish', hx_wrap(views.recode_finish), name='recode.finish'),
]

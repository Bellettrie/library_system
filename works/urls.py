from django.urls import path

from works.views import WorkList
from . import views

urlpatterns = [
    path('search', WorkList.as_view(), name='works.list'),
    path('<slug:pk>', views.WorkDetail.as_view(), name='work.view'),
]
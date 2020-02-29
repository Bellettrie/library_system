from django.urls import path

from works.views import WorkList
from . import views

urlpatterns = [
    path('search', WorkList.as_view(), name='search-works'),

    path('<slug:pk>', views.WorkDetail.as_view(), name='show'),
]
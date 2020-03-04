from django.urls import path
from lendings.permissions import VIEW, permits

from members.permissions import authorize
from . import views

urlpatterns = [
    path('', views.index, name='lending_base'),
    path('work/<int:work_id>', views.work_based, name='lend_from_work'),
    path('finalize/<int:work_id>/<int:member_id>', views.finalize, name='finalize_lending'),
    path('me/', authorize(VIEW, permits)(views.me), name='my-list')
]
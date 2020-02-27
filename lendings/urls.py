from django.urls import path

from members.views import MemberList
from . import views

urlpatterns = [
    path('', MemberList.as_view(), name='members-list'),
    path('work/<int:work_id>', views.work_based, name='lend_from_work'),
    path('finalize/<int:work_id>/<int:member_id>', views.finalize, name='finalize_lending'),
]
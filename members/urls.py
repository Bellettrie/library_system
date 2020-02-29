from django.urls import path

from members.views import MemberList
from . import views

urlpatterns = [
    path('', MemberList.as_view(), name='index'),
    path('<int:member_id>', views.show, name='show_member'),
    path('<int:member_id>/edit', views.edit, name='edit_member'),
    path('new', views.new, name='new_member'),

]
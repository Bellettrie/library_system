from django.urls import path

from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT
from members.views import MemberList, signup, delete_user, change_user, remove_user
from . import views

urlpatterns = [

    path('search/<search_text>', views.get_authors_by_query, name='authors.query'),
    path('list', views.CreatorList.as_view(), name='creator.list'),
    path('view/<int:creator_id>', views.show, name='creator.view'),
    path('delete/<int:creator_id>', views.delete, name='creator.delete'),
    path('edit/<int:creator_id>', views.edit, name='creator.edit'),
    path('new/', views.edit, name='creator.new'),
]

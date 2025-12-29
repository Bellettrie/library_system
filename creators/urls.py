from django.urls import path

from . import views

urlpatterns = [

    path('search/<search_text>', views.get_authors_by_query, name='creators.query'),
    path('list', views.CreatorList.as_view(), name='creators.list'),

    path('new/', views.edit, name='creators.new'),
    path('<int:creator_id>', views.show, name='creators.view'),
    path('<int:creator_id>/delete', views.delete, name='creators.delete'),
    path('<int:creator_id>/edit', views.edit, name='creators.edit'),
]

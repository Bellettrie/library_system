from django.urls import path

from . import views

urlpatterns = [

    path('search/<search_text>', views.get_authors_by_query, name='creator.query'),
    path('list', views.CreatorList.as_view(), name='creator.list'),

    path('new/', views.edit, name='creator.new'),
    path('<int:creator_id>', views.show, name='creator.view'),
    path('<int:creator_id>/delete', views.delete, name='creator.delete'),
    path('<int:creator_id>/edit', views.edit, name='creator.edit'),
]

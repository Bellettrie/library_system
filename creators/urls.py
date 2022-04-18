from django.urls import path

from . import views

urlpatterns = [

    path('search/<search_text>', views.get_authors_by_query, name='authors.query'),
    path('list', views.CreatorList.as_view(), name='creator.list'),
    path('view/<int:creator_id>', views.show, name='creator.view'),
    path('delete/<int:creator_id>', views.delete, name='creator.delete'),
    path('edit/<int:creator_id>', views.edit, name='creator.edit'),
    path('new/', views.edit, name='creator.new'),
    path('collisions/', views.collisions, name='creator.collides'),
]

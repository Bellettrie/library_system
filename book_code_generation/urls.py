from django.urls import path

from . import views

urlpatterns = [

    path('generate/<slug:publication_id>/<slug:location_id>', views.get_book_code, name='book_code.generate'),

    path('generate/creator/<slug:creator_id>/<slug:location_id>', views.get_creator_number,
         name='book_code.generate_creator_number'),
    path('codes', views.show_letter_list, name='book_code.code_list'),
]

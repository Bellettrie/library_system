from django.urls import path

from members.permissions import MEMBERS_LIST, MEMBERS_NEW, MEMBERS_VIEW, MEMBERS_EDIT
from members.views import MemberList, signup, delete_user, change_user, remove_user

from . import views

urlpatterns = [

    path('generate/<slug:publication_id>/<slug:location_id>', views.get_book_code, name='book_code.generate'),
    path('generate_series/<slug:series_id>/<slug:location_id>', views.get_book_code_series, name='book_code.generate_series'),
    path('generate_creator/<slug:creator_id>/<slug:location_id>', views.get_creator_number, name='book_code.generate_creator_number'),

]

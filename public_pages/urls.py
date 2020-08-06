from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND, LENDING_FAILED

from . import views
from .views import view_page

urlpatterns = [
    path('', view_page('', ''), name='homepage'),

]

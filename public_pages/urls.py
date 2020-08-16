from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND, LENDING_FAILED

from . import views
from .views import view_page, view_named_page, render_page_from_request, test_render_function, edit_named_page, new_named_page
def fun(request):
    pass
urlpatterns = [
    path('testRender', test_render_function, name='render_test_page'),

    path('render', render_page_from_request, name='render_test'),
    path('<page_name>/<sub_page_name>/edit', edit_named_page, name='edit_named_page'),
    path('<page_name>/<sub_page_name>', view_named_page, name='named_page'),
    path('new_page', new_named_page, name='new_named_page'),
    path('new_page_group', fun, name='new_named_group'),
    path('list_all', fun, name='new_named_group'),
]

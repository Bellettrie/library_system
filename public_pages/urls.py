from django.urls import path

from utils.wrappers import hx_wrap
from . import views
from .views import view_named_page, render_page_from_request, test_render_function, edit_named_page, \
    new_named_page, list_named_pages, delete_page, list_uploads, new_upload, delete_upload, view_index_page


def fun(request):
    pass


urlpatterns = [
    path('testRender', test_render_function, name='render_test_page'),
    path('uploads', list_uploads, name='list_uploads'),
    path('uploads/new', new_upload, name='new_upload'),
    path('uploads/delete/<pk>', delete_upload, name='delete_upload'),
    path('render', render_page_from_request, name='render_test'),
    path('list', list_named_pages, name='list_pages'),

    path('new_page_group', fun, name='new_named_group'),

    path('<page_name>', view_index_page, name='index_page'),
    path('<page_group_name>/new', new_named_page, name='new_named_page'),

    path('<page_group_name>/<page_name>', view_named_page, name='named_page'),
    path('<page_group_name>/<page_name>/edit', edit_named_page, name='edit_named_page'),
    path('<pk>/delete', hx_wrap(delete_page), name='delete_named_page'),

]

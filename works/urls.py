from django.urls import path

from utils.wrappers import hx_wrap
from works.views import WorkList, create_item_state, item_edit, edit_work, publication_new, \
    item_new, \
    item_history, change_item_location, publication_view, work_ask_delete
from . import views

urlpatterns = [
    path('new', publication_new, name='works.publication.new'),

    path('search', WorkList.as_view(), name='works.list'),
    path('search/json', views.search_works_json, name='works.list.json'),

    path('<slug:work_id>', publication_view, name='works.view'),
    path('<slug:work_id>/edit', edit_work, name='works.edit'),
    path('<slug:work_id>/ask_delete/<slug:return_to>', hx_wrap(work_ask_delete), name='works.delete.ask'),
    path('<slug:work_id>/delete', views.delete_work, name='works.delete'),

    path('<slug:work_id>/item/new/', item_new, name='works.item.new'),
    path('item/<slug:item_id>/edit', item_edit, name='works.item.edit'),
    path('item/<slug:item_id>/location_change', hx_wrap(change_item_location), name='works.item.change_location'),
    path('itemhistory/<slug:item_id>', hx_wrap(item_history), name='works.item.state.list'),
    path('itemhistory/new/<slug:item_id>', hx_wrap(create_item_state), name='works.item.state.new'),

    path('<slug:work_id>/relation/<slug:relation_id>/remove', hx_wrap(views.remove_relation),
         name='works.relation.delete'),
    path('<slug:work_id>/relation/<slug:relation_id>/edit', views.edit_relation_to_work,
         name='works.relation.edit'),
    path('<slug:work_id>/relation/<slug:relation_id>/edit/rev', views.edit_relation_from_work,
         name='works.relation.edit.rev'),

    path('subworks/new/<slug:work_id>', views.subwork_new, name='works.subwork.new'),
    path('subworks/edit/<slug:work_id>', views.subwork_edit, name='works.subworks.edit'),
]

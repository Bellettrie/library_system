from django.urls import path

from utils.wrappers import hx_wrap
from works.views import WorkList, create_item_state, item_edit, publication_edit, publication_new, \
    item_new, \
    item_history, change_item_location
from . import views

urlpatterns = [
    path('search', WorkList.as_view(), name='works.list'),
    path('search/json', views.search_works_json, name='works.list.json'),

    path('item/<slug:item_id>/edit', item_edit, name='works.item.edit'),
    path('item/new/<slug:publication_id>', item_new, name='works.item.new'),

    path('itemhistory/<slug:item_id>', hx_wrap(item_history), name='works.item.states'),

    path('itemhistory/new/<slug:item_id>', hx_wrap(create_item_state), name='works.item_state.create'),
    path('item/<slug:item_id>/location_change', hx_wrap(change_item_location), name='works.item.change_location'),

    path('work/<slug:work_id>/relation/<slug:relation_id>/remove', hx_wrap(views.remove_relation),
         name='works.relation.remove'),
    path('work/<slug:work_id>/relation/<slug:relation_id>/edit', views.edit_relation_to_work,

         name='works.relation.edit'),
    path('work/<slug:work_id>/relation/<slug:relation_id>/edit/rev', views.edit_relation_from_work,
         name='works.relation.edit.rev'),

    path('publication/edit/<slug:publication_id>', publication_edit, name='works.publication.edit'),
    path('publication/new', publication_new, name='works.publication.new'),
    path('publication/<slug:pk>', views.WorkDetail.as_view(), name='work.view'),

    path('subworks/new/<slug:publication_id>', views.subwork_new, name='work.subwork.new'),
    path('subworks/edit/<slug:subwork_id>', views.subwork_edit, name='work.subwork.edit'),
    path('subworks/delete/<slug:subwork_id>', views.subwork_delete, name='work.subwork.delete'),
]

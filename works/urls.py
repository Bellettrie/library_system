from django.urls import path

from works.views import WorkList, create_item_state, create_item_state_hx, item_edit, publication_edit, publication_new, item_new, \
    item_history, item_history_hx
from . import views

urlpatterns = [
    path('search', WorkList.as_view(), name='works.list'),

    path('item/<slug:item_id>', item_edit, name='works.item.edit'),
    path('item/new/<slug:publication_id>', item_new, name='works.item.new'),

    path('itemhistory/<slug:item_id>', item_history, name='works.item.states'),
    path('itemhistory/hx/<slug:item_id>', item_history_hx, name='works.item.states_hx'),

    path('itemhistory/new/<slug:item_id>', create_item_state, name='works.item_state.create'),
    path('itemhistory/new/hx/<slug:item_id>', create_item_state_hx, name='works.item_state.create_hx'),

    path('publication/edit/<slug:publication_id>', publication_edit, name='works.publication.edit'),
    path('publication/new', publication_new, name='works.publication.new'),
    path('publication/<slug:pk>', views.WorkDetail.as_view(), name='work.view'),

    path('subworks/new/<slug:publication_id>', views.subwork_new, name='work.subwork.new'),
    path('subworks/edit/<slug:subwork_id>', views.subwork_edit, name='work.subwork.edit'),
    path('subworks/delete/<slug:subwork_id>', views.subwork_delete, name='work.subwork.delete'),
]

from django.urls import path

from works.views import WorkList, create_item_state
from . import views

urlpatterns = [
    path('search', WorkList.as_view(), name='works.list'),
    path('item_state/<slug:item_id>', create_item_state, name='works.item_state.create'),
    path('<slug:pk>', views.WorkDetail.as_view(), name='work.view'),
]

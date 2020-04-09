from django.urls import path

from lendings.path_names import LENDING_VIEW, LENDING_LIST, LENDING_NEW_WORK, LENDING_FINALIZE, \
    LENDING_MY_LENDINGS, LENDING_NEW_MEMBER, LENDING_RETURNBOOK, LENDING_EXTEND

from . import views
from .views import index

urlpatterns = [
    path('', index, name=LENDING_LIST),
    path('work/<int:work_id>', views.work_based, name=LENDING_NEW_WORK),
    path('member/<int:member_id>', views.member_based, name=LENDING_NEW_MEMBER),
    path('finalize/<int:work_id>/<int:member_id>', views.finalize, name=LENDING_FINALIZE),
    path('extend/<int:work_id>', views.extend, name=LENDING_EXTEND),
    path('return/<int:work_id>', views.returnbook, name=LENDING_RETURNBOOK),
    path('me/', views.me, name=LENDING_MY_LENDINGS),

]


from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.models.lending import Lending

from members.models import Member

from works.models import Item
from works.views import get_works


from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from lendings.models.lending import Lending


@permission_required('lendings.add_lending')
def index(request):
    lendings = Lending.objects.filter(handed_in=False).order_by('end_date')
    return render(request, 'lending_list.html', {'lendings': lendings})

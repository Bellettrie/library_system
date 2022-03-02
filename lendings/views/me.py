
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



@login_required()
def me(request):
    return render(request, 'lending_detail.html', {"member": request.user.member})

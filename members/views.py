from django.shortcuts import render
from .models import Member

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, 'members_base.html', {'members': Member.objects.all()})


def show(request, member_id):
    return render(request, 'member_show.html', {'member': Member.objects.get(pk=member_id)})

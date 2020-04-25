from datetime import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from utils.get_query_words import get_query_words
from .models import Member
from .forms import EditForm

# Create your views here.
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import user_passes_test, login_required, permission_required


class MemberList(PermissionRequiredMixin, ListView):
    permission_required = 'members.view_member'
    model = Member
    template_name = 'member_list.html'
    paginate_by = 50

    def get_queryset(self):  # new
        words = get_query_words(self.request)
        if words is None:
            return []
        if len(words) == 0:
            return Member.objects.filter(is_anonymous_user=False).filter(
                Q(end_date__gte=datetime.now()) | Q(end_date__isnull=True))

        result_set = None
        for word in words:
            members = Member.objects.filter(name__icontains=word)

            if result_set is None:
                result_set = members
            else:
                result_set = result_set & members

        return list(set(result_set))


@permission_required('members.view_member')
def show(request, member_id):
    return render(request, 'member_detail.html', {'member': Member.objects.get(pk=member_id)})


@permission_required('members.change_member')
def edit(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = EditForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('members.view', args=(member_id,)))
    else:
        form = EditForm(instance=member)
    return render(request, 'member_edit.html', {'form': form, 'member': member})


@permission_required('members.add_member')
def new(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('members', args=(instance.pk,)))
    else:
        form = EditForm()
    return render(request, 'member_edit.html', {'form': form})


@permission_required('auth.add_user')
def signup(request, member_id):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save()

            instance.member = Member.objects.get(pk=member_id)
            instance.member.user = instance
            instance.member.save()
            instance.save()
            return HttpResponseRedirect(reverse('members.view', args=(instance.member.pk,)))
    else:
        form = UserCreationForm()
    return render(request, 'user_edit.html', {'form': form, 'member': Member.objects.get(pk=member_id)})


@permission_required('auth.delete_user')
def delete_user(request, member_id):
    member = Member.objects.get(pk=member_id)
    member.user.delete()
    member.user = None
    member.save()

    return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))

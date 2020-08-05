import random
import string
from datetime import datetime

from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView

from bellettrie_library_system.settings import BASE_URL
from mail.models import mail_member
from utils.get_query_words import get_query_words
from .models import Member
from .forms import EditForm

# Create your views here.
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import permission_required


class MemberList(PermissionRequiredMixin, ListView):
    permission_required = 'members.view_member'
    model = Member
    template_name = 'member_list.html'
    paginate_by = 50

    def get_queryset(self):  # new
        words = get_query_words(self.request)
        get_previous = self.request.GET.get('previous', False)

        if words is None:
            return []
        if len(words) == 0:
            m = Member.objects.filter(is_anonymous_user=False)
            if not get_previous:
                m = m.filter(Q(end_date__gte=datetime.now()) | Q(end_date__isnull=True))
            return m

        result_set = None
        for word in words:
            members = Member.objects.filter(Q(name__icontains=word) | Q(nickname__icontains=word))
            if not get_previous:
                members = members.filter(Q(end_date__gte=datetime.now()) | Q(end_date__isnull=True))

            if result_set is None:
                result_set = members
            else:
                result_set = result_set & members

        return list(set(result_set))


def show(request, member_id):
    if not request.user.has_perm('members.view_member'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member.pk == member_id):
            raise PermissionDenied
    return render(request, 'member_detail.html', {'member': Member.objects.get(pk=member_id)})


@permission_required('members.change_member')
def edit(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = EditForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            if request.user.has_perm('committee_update'):
                member.update_groups()
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
            if request.user.has_perm('committee_update'):
                instance.update_groups()
            return HttpResponseRedirect(reverse('members', args=(instance.pk,)))
    else:
        form = EditForm()
    return render(request, 'member_edit.html', {'form': form})


def signup(request, member_id):
    member = Member.objects.get(pk=member_id)
    if not request.user.has_perm('auth.add_user'):
        members = Member.objects.filter(pk=member_id, invitation_code=request.GET.get('key', ''))

        if len(members) != 1:
            raise PermissionDenied
        if not members[0].invitation_code_valid:
            raise PermissionDenied
        else:
            print(members[0].invitation_code)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save()

            instance.member = member
            instance.member.user = instance
            instance.member.invitation_code_valid = False
            instance.member.save()
            instance.save()
            return HttpResponseRedirect(reverse('members.view', args=(instance.member.pk,)))
    else:
        form = UserCreationForm()
    return render(request, 'user_create.html', {'form': form, 'member': member})


@permission_required('auth.change_user')
def change_user(request, member_id):
    member = Member.objects.get(pk=member_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user=member.user, data=request.POST)
        if form.is_valid():
            instance = form.save()

            instance.member = member
            instance.member.user = instance
            instance.member.save()
            instance.save()
            return HttpResponseRedirect(reverse('members.view', args=(instance.member.pk,)))
    else:
        form = PasswordChangeForm(member.user)
    return render(request, 'user_edit.html', {'form': form, 'member': member, 'user': member.user})


@permission_required('auth.delete_user')
def remove_user(request, member_id):
    member = Member.objects.get(pk=member_id)
    return render(request, 'user_delete.html', {'member': member, 'user': member.user})


@permission_required('auth.delete_user')
def delete_user(request, member_id):
    member = Member.objects.get(pk=member_id)
    user = member.user
    member.user = None
    member.save()
    user.delete()

    return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))


@permission_required('auth.add_user')
def generate_invite_code(request, member_id):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(16))
    member = Member.objects.get(pk=member_id)
    if member.user:
        member.invitation_code_valid = False
        member.save()

        return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))
    member.invitation_code = result_str
    member.invitation_code_valid = True
    mail_member('mails/invitation.tpl', {'member': member}, member, True)
    member.save()

    return render(request, 'member_detail.html', {'member': member, 'extra': "Invitation mail sent"})


@permission_required('auth.add_user')
def disable_invite_code(request, member_id):
    member = Member.objects.get(pk=member_id)
    member.invitation_code_valid = False
    member.save()
    return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))

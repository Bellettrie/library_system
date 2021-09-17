import random
import string
from datetime import datetime

from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView

from bellettrie_library_system.settings import BASE_URL
from mail.models import mail_member
from utils.get_query_words import get_query_words
from .models import Member, MembershipPeriod
from .forms import EditForm, MembershipPeriodForm

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.decorators import permission_required


def query_members(words, get_previous=False):
    msps = MembershipPeriod.objects.filter((Q(start_date__isnull=True) | Q(start_date__lte=datetime.now()))
                                           & (Q(end_date__isnull=True) | Q(end_date__gte=datetime.now())))

    if words is None:
        return []
    if len(words) == 0:
        m = Member.objects.filter(is_anonymous_user=False)
        if not get_previous:
            m = m.filter(membershipperiod__in=msps)
        return m

    result_set = None
    for word in words:
        members = Member.objects.filter(Q(name__icontains=word) | Q(nickname__icontains=word))
        if not get_previous:
            members = members.filter(membershipperiod__in=msps)

        if result_set is None:
            result_set = members
        else:
            result_set = result_set & members

    return list(set(result_set))


class MemberList(PermissionRequiredMixin, ListView):
    permission_required = 'members.view_member'
    model = Member
    template_name = 'member_list.html'
    paginate_by = 50

    def get_queryset(self):  # new
        words = get_query_words(self.request.GET.get("q"))
        return query_members(words, self.request.GET.get('previous', False))

class AnonMemberList(PermissionRequiredMixin, ListView):
    permission_required = 'members.view_member'
    model = Member
    template_name = 'member_anonymisable.html'
    paginate_by = 50

def show(request, member_id):
    if not request.user.has_perm('members.view_member'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member.pk == member_id):
            raise PermissionDenied
    member = get_object_or_404(Member, pk=member_id)
    if member.is_anonimysed:
        return render(request, 'member_detail_anonymous.html', {'member': member})
    return render(request, 'member_detail.html', {'member': member})

@transaction.atomic
@permission_required('members.change_member')
def edit(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    can_change = request.user.has_perm('members.change_committee')
    edit_dms = request.user.has_perm('members.change_committee')
    if request.method == 'POST':
        form = EditForm(can_change, edit_dms, request.POST, instance=member)
        if form.is_valid():
            if not can_change and 'committees' in form.changed_data:
                raise ValueError("Wrong")
            form.save()
            if can_change:
                member.update_groups()
            return HttpResponseRedirect(reverse('members.view', args=(member_id,)))
    else:
        form = EditForm(can_change, edit_dms, instance=member)
    return render(request, 'member_edit.html', {'form': form, 'member': member})

def get_end_date(year, month_second_half):
    if month_second_half:
        year += 1
    return str(year) + "-06-30"

@transaction.atomic
@permission_required('members.add_member')
def new(request):
    can_change = request.user.has_perm('members.change_committee')
    edit_dms = request.user.has_perm('members.change_committee')
    if request.method == 'POST':
        form = EditForm(can_change, edit_dms, request.POST)
        if form.is_valid() and request.POST.get('end_date'):
            if not can_change and 'committees' in form.changed_data:
                raise ValueError("Wrong")
            instance = form.save()
            inst = MembershipPeriodForm(request.POST).save(commit=False)
            inst.member = instance
            inst.save()
            if can_change:
                instance.update_groups()
            return HttpResponseRedirect(reverse('members.view', args=(instance.pk,)))
        else:
            return render(request, 'member_edit.html', {'form': form, 'new': True, 'error': "No end date specified",
                                                        'md_form': MembershipPeriodForm(request.POST)})
    else:
        form = EditForm(can_change, edit_dms)
    md_form = MembershipPeriodForm(initial={'start_date': datetime.date(datetime.now()),
                                            'end_date': get_end_date(datetime.now().year,
                                                                     datetime.now().month > 6)})
    return render(request, 'member_edit.html', {'form': form, 'new': True, 'md_form': md_form})

@transaction.atomic
def signup(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
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
            instance.member.update_groups()
            instance.member.save()
            instance.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = UserCreationForm()
    return render(request, 'user_create.html', {'form': form, 'member': member})

@transaction.atomic
@permission_required('auth.change_user')
def change_user(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
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

@transaction.atomic
@permission_required('auth.delete_user')
def remove_user(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    return render(request, 'user_delete.html', {'member': member, 'user': member.user})

@transaction.atomic
@permission_required('auth.delete_user')
def delete_user(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    user = member.user
    member.user = None
    member.save()
    user.delete()

    return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))

@transaction.atomic
@permission_required('auth.add_user')
def generate_invite_code(request, member_id):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(16))
    member = get_object_or_404(Member, pk=member_id)
    if member.user:
        member.invitation_code_valid = False
        member.save()

        return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))
    member.invitation_code = result_str
    member.invitation_code_valid = True
    mail_member('mails/invitation.tpl', {'member': member}, member, True)
    member.save()

    return render(request, 'member_detail.html', {'member': member, 'extra': "Invitation mail sent"})

@transaction.atomic
@permission_required('auth.add_user')
def disable_invite_code(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    member.invitation_code_valid = False
    member.save()
    return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))

@transaction.atomic
@permission_required('members.change_member')
def edit_membership_period(request, membership_period_id):
    member = get_object_or_404(MembershipPeriod, pk=membership_period_id)
    if request.method == 'POST':

        form = MembershipPeriodForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            member.member.try_and_delete_double_periods()
            return HttpResponseRedirect(reverse('members.view', args=(member.member.pk,)))
    else:
        form = MembershipPeriodForm(instance=member)

    return render(request, 'member_membership_edit.html', {'form': form, 'member': member})

@transaction.atomic
@permission_required('members.change_member')
def new_membership_period(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':

        form = MembershipPeriodForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.member = member
            instance.save()
            member.try_and_delete_double_periods()

            return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))
    else:
        form = MembershipPeriodForm(instance=member, initial={'start_date': datetime.date(datetime.now()),
                                                              'end_date': get_end_date(datetime.now().year,
                                                                                       datetime.now().month > 6)})
    return render(request, 'member_membership_edit.html', {'form': form, 'member': member})

@transaction.atomic
@permission_required('members.delete_member')
def delete_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete member with name " + member.name})
    member = get_object_or_404(Member, pk=member_id)
    MembershipPeriod.objects.filter(member=member).delete()
    from mail.models import MailLog
    anonymous_members = list(Member.objects.filter(is_anonymous_user=True))
    member.destroy(MailLog.objects.filter(member=member), 'member', anonymous_members, False)
    member.delete()

    return HttpResponseRedirect(reverse('members.list'))

@transaction.atomic
@permission_required('members.delete_member')
def anonymise(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "anonymise member with name " + member.name})
    member.anonymise_me(dry_run=False)

    return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))

@transaction.atomic
@permission_required('members.delete_member')
def anonymise_list(request):
    # return HttpResponse("HI")
    errors = []
    for member_pk in request.POST.getlist('member'):
        member = Member.objects.get(pk=member_pk)
        if member.should_be_anonymised():
            member.anonymise_me(dry_run=False)
            if member.can_be_deleted():
                member.delete()
        else:
            errors.append(member)
    if len(errors) > 0:
        return HttpResponse(" ".join(errors))
    return HttpResponseRedirect(reverse('members.list.anon'))

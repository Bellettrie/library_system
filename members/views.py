from datetime import datetime

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
    template_name = 'members_list.html'
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
    return render(request, 'members_view.html', {'member': Member.objects.get(pk=member_id)})


def edit(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = EditForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            member.update_groups()
            return HttpResponseRedirect(reverse('members.view', args=(member_id,)))
    else:
        form = EditForm(instance=member)
    return render(request, 'member_edit.html', {'form': form, 'member': member})


def new(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('show_member', args=(instance.pk,)))
    else:
        form = EditForm()
    return render(request, 'member_edit.html', {'form': form})

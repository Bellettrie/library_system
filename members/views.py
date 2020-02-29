from datetime import datetime

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView

from utils.get_query_words import get_query_words
from .models import Member
from .forms import EditForm

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect


class MemberList(ListView):
    model = Member
    template_name = 'members_base.html'
    paginate_by = 50

    def get_queryset(self):  # new
        words = get_query_words(self.request)
        if words is None:
            return []
        if len(words) == 0:
            return Member.objects.filter(is_anonymous_user=False).filter(Q(end_date__gte=datetime.now()) | Q(end_date__isnull=True))

        result_set = None
        for word in words:
            members = Member.objects.filter(name__icontains=word)

            if result_set is None:
                result_set = members
            else:
                result_set = result_set & members

        return list(set(result_set))


def show(request, member_id):
    return render(request, 'member_show.html', {'member': Member.objects.get(pk=member_id)})


def edit(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('show_member', args=(member_id,)))
    else:
        form = EditForm(instance=member)
    return render(request, 'member_edit.html', {'form': form, 'member': member})

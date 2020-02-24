from datetime import datetime

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView

from .models import Member
from .forms import EditForm

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect


class MemberList(ListView):
    model = Member
    template_name = 'members_base.html'
    paginate_by = 50


    def get_queryset(self):  # new

        query = self.request.GET.get('q')
        if query is None:
            return []
        p_words = query.split(" ")
        words = []
        for word in p_words:
            if len(word) > 2:
                words.append(word)
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
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('show_member', args=(member_id,)))
    else:
        question = get_object_or_404(Member, pk=member_id)
        form = EditForm(question)
    return render(request, 'member_edit.html', {'member': question, 'form': form})

def save(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    member.notes = request.POST['notes']
    member.save()
    return HttpResponseRedirect(reverse('show_member', args=(member_id,)))
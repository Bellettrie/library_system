from datetime import datetime

from django.shortcuts import render
from django.views.generic import ListView

from .models import Member

# Create your views here.
from django.http import HttpResponse


class MemberList(ListView):
    model = Member
    template_name = 'members_base.html'
    paginate_by = 30


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
            return Member.objects.filter(end_date__gte=datetime.now())

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

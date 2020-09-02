import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

# Create your views here.
from members.models import Member


@permission_required('members.view_member')
def show_mail_addresses(request):
    print(request.GET)
    members = Member.objects.all()
    found_members = []
    r_str = ""

    if request.GET.get('exec'):
        if request.GET.get('m_after'):
            for member in members:
                d = datetime.date.fromisoformat(request.GET.get('m_after'))
                if member.end_date is not None and member.end_date > d:
                    found_members.append(member)
        else:
            found_members = list(members)

        if request.GET.get('m_before'):
            found_2 = []
            for member in found_members:
                d = datetime.date.fromisoformat(request.GET['m_before'])
                if member.end_date is not None and member.end_date < d:
                    found_2.append(member)
            found_members = found_2
        if request.GET.get('m_include_honorary', False):
            for member in members:
                if member.end_date is None:
                    found_members.append(member)
        for member in found_members:
            if len(member.email) > 0:
                r_str += ("; " + member.email)
    return render(request, 'data-mining-list.html', {'member_mail_addresses': r_str})

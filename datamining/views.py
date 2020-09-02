import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

# Create your views here.
from members.models import Member, Committee


def fetch_date(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return datetime.date(dt.year,dt.month,dt.day)


@permission_required('members.view_member')
def show_mail_addresses(request):
    print(request.GET)
    members = Member.objects.all()
    committees = Committee.objects.all()
    found_members = []
    r_str = ""

    if request.GET.get('exec'):
        found_committees = request.GET.getlist('committees')
        if request.GET.get('m_after'):
            for member in members:
                d = fetch_date(request.GET.get('m_after'))
                if member.end_date is not None and member.end_date > d:
                    found_members.append(member)
        else:
            found_members = list(members)

        if request.GET.get('m_before'):
            found_2 = []
            for member in found_members:
                d = fetch_date(request.GET['m_before'])
                if member.end_date is not None and member.end_date < d:
                    found_2.append(member)
            found_members = found_2
        if request.GET.get('m_include_honorary', False):
            for member in members:
                if member.end_date is None:
                    found_members.append(member)
        if len(found_committees) > 0:
            found_2 = []
            for member in found_members:
                found = False
                for committee in member.committees.all():
                    if str(committee.pk) in found_committees:
                        found = True
                if found:
                    found_2.append(member)
            found_members = found_2
        for member in found_members:
            if len(member.email) > 0:
                r_str += ("; " + member.email)
    return render(request, 'data-mining-list.html', {'member_mail_addresses': r_str, 'committees': committees})

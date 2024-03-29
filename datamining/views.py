import datetime

from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from datamining.procedures.filter_members import filter_members
from datamining.procedures.get_lending_stats import get_lending_stats
from lendings.models import Lending
from members.models import Member, Committee, MembershipPeriod, MembershipType, MemberBackground
from utils.time import get_today


def fetch_date(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return datetime.date(dt.year, dt.month, dt.day)


def find_members_by_request(request):
    if request.GET.get('exec'):
        found_committees = request.GET.getlist('committees')
        found_privacy_settings = request.GET.getlist('privacy')
        before_date = fetch_date(request.GET.get('m_before') or "1900-01-01")
        after_date = fetch_date(request.GET.get('m_after') or "9999-12-31")
        include_honorary = request.GET.get('m_include_honorary', False)
        filter_only_blacklisted = request.GET.get("m_filter_only_blacklisted", False)
        dms = request.GET.get('dms', False)

        return filter_members(found_committees,
                              found_privacy_settings,
                              before_date,
                              after_date,
                              include_honorary,
                              filter_only_blacklisted, dms)
    return Member.objects.none()


@permission_required('members.view_member')
def show_members(request):
    committees = Committee.objects.all()
    found_members = find_members_by_request(request)
    member_mails = []

    for member in found_members:
        if len(member.email) > 0:
            member_mails.append(member.email)

    return render(request, 'datamining/member_filtering.html',
                  {'mails': request.GET.get('mails'), 'member_mail_addresses': "; ".join(member_mails), 'dms': request.GET.get('dms'),
                   'members': found_members, 'committees': committees})


def get_member_statistics(day):
    members = MembershipPeriod.objects.filter(
        (Q(start_date__lte=day) & Q(end_date__gte=day)) | Q(end_date__isnull=True))
    quadrants = dict()
    member_bg_counts = dict()
    member_type_counts = dict()
    r_mem = []
    for member in members:
        count = quadrants.get((member.member_background, member.membership_type), 0)
        quadrants[(member.member_background, member.membership_type)] = count + 1
        count = member_bg_counts.get(member.member_background, 0)
        member_bg_counts[member.member_background] = count + 1
        count = member_type_counts.get(member.membership_type, 0)
        member_type_counts[member.membership_type] = count + 1
        if member.membership_type is not None and member.member_background.name == 'employee':
            r_mem.append(member)

    zz = dict()
    for ru in MemberBackground.objects.all():
        zz[ru] = dict()
    zz[None] = dict()

    for ru in zz:
        for a in MembershipType.objects.all():
            zz[ru][a] = 0
        zz[ru][None] = 0

    for quad in quadrants.keys():
        row = zz.get(quad[0], dict())
        row[quad[1]] = quadrants[quad]
        zz[quad[0]] = row

    col_counts = dict()
    for row in zz.keys():
        if row is None:
            continue
        r_count = 0
        for z in zz[row].keys():
            if z is None:
                continue
            r_count += zz[row][z]
            col_counts[z] = col_counts.get(z, 0) + zz[row][z]
        zz[row]['Total'] = r_count
        col_counts['Total'] = col_counts.get('Total', 0) + r_count

    for row in zz.keys():
        zz[row].pop(None)
    zz.pop(None)
    zz['Total'] = col_counts
    return zz


@permission_required('members.view_member')
def show_membership_stats(request):
    dat = request.GET.get('date', get_today().isoformat())
    if dat == "":
        dat = get_today().isoformat()
    q = get_member_statistics(dat)
    return render(request, 'datamining/member_stats.html', {'q': q})


@permission_required('works.view_work')
def show_lending_stats(request):
    start_date = request.GET.get('start_date', "1583-01-01")
    end_date = request.GET.get('end_date', get_today().isoformat())
    if start_date == "":
        # 1583 is the first year allowed by default
        start_date = "1583-01-01"
    if end_date == "":
        end_date = get_today().isoformat()
    q = get_lending_stats(start_date, end_date)
    return render(request, 'datamining/lending_stats.html', {'q': q})

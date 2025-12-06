from django.http import HttpResponse
from members.models import Committee


def webcie(request):
    return by_committee(request, "WEB")


def by_committee(request, committee_code):
    committee = Committee.objects.filter(code=committee_code).first()
    if hasattr(request.user, 'member') and committee in request.user.member.committees.all():
        return HttpResponse(status=200)
    return HttpResponse(content='<meta http-equiv="refresh" content="0;URL=\'/accounts/login/?next=/dev/\'">', status=403)
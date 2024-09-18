from django.http import HttpResponse
from members.models import Committee


def webcie(request):
    committee = Committee.objects.filter(name__exact="Web Committee").first()
    if hasattr(request.user, 'member') and committee in request.user.member.committees.all():
        return HttpResponse(status=200)
    return HttpResponse(content='  <meta http-equiv="refresh" content="0;URL=\'/accounts/login/?next=/dev/\'">', status=403)

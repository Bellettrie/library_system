from django.http import HttpResponse
from members.models import Committee


def webcie(request):
    committee = Committee.objects.filter(name__exact="Web Committee").first()
    if hasattr(request.user, 'member') and committee in request.user.member.committees.all():
        return HttpResponse(status=200)
    return HttpResponse(status=403)

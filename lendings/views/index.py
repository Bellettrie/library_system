from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from lendings.models.lending import Lending


@permission_required('lendings.add_lending')
def index(request):
    lendings = Lending.objects.filter(handed_in=False).order_by('end_date')
    return render(request, 'lendings/list.html', {'lendings': lendings})

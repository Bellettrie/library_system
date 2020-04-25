from django.shortcuts import render

# Create your views here.
from inventarisation.models import Inventarisation
from works.models import Item


def list_inventarisations(request):
    inventarisations = Inventarisation.objects.all()
    return render(request, "inventarisation_list.html", {'inventarisations': inventarisations})


def print_list(request, inventarisation_id):
    inventarisation = Inventarisation.objects.get(pk=inventarisation_id)

    items = Item.objects.filter(location=inventarisation.location).order_by('signature')
    groups = []
    counter = 0

    for item in items:
        if counter == 0:
            groups.append([])
            counter = 10
        groups[len(groups )-1].append(item)
        counter -= 1
    return render(request, "inventarisation_print_list.html", {'groups': groups})

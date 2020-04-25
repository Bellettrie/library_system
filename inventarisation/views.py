from django.conf.urls import url
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from inventarisation.models import Inventarisation
from works.models import Item, ItemState, Location


def list_inventarisations(request):
    inventarisations = Inventarisation.objects.order_by('-is_active', '-dateTime')
    return render(request, "inventarisation_list.html", {'inventarisations': inventarisations})


def get_groups(inventarisation):
    items = Item.objects.filter(location=inventarisation.location).order_by('signature')
    groups = []
    counter = 0

    for item in items:
        if counter == 0:
            groups.append([])
            counter = 10
        groups[len(groups) - 1].append(item)
        counter -= 1
    return groups


def print_list(request, inventarisation_id):
    inventarisation = Inventarisation.objects.get(pk=inventarisation_id)
    groups = get_groups(inventarisation)
    return render(request, "inventarisation_print_list.html", {'groups': groups})


class InventarisationCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'config.add_inventarisation'
    model = Inventarisation
    fields = ['location']
    template_name = 'inventarisation_new.html'
    success_url = reverse_lazy('inventarisation.list')


def inventarisation_form(request, inventarisation_id, page_id):
    inventarisation = Inventarisation.objects.get(pk=inventarisation_id)
    group = get_groups(inventarisation)[int(page_id)]
    if request.method == "POST":
        for z in request.POST:
            if z.startswith('seen'):
                code = int(z[4:])
                if request.POST[z] == "yes":
                    try:
                        item_state = ItemState.objects.get(item_id=code, inventarisation=inventarisation)
                        item_state.type = "AVAILABLE"
                        item_state.save()
                    except ItemState.DoesNotExist:
                        ItemState.objects.create(item_id=code, type="AVAILABLE", inventarisation=inventarisation)
                elif request.POST[z] == "no":
                    try:
                        item_state = ItemState.objects.get(item_id=code, inventarisation=inventarisation)
                        item_state.type = "MISSING"
                        item_state.save()
                    except ItemState.DoesNotExist:
                        ItemState.objects.create(item_id=code, type="MISSING", inventarisation=inventarisation)
                else:
                    ItemState.objects.filter(item_id=code, inventarisation=inventarisation).delete()
        if request.POST.get("next"):
            return get_inventarisation_next(request, inventarisation_id, page_id)


    pre_filled = {}
    for item in group:
        try:
            pre_filled[item] = ItemState.objects.get(item=item, inventarisation=inventarisation).type
        except ItemState.DoesNotExist:
            pass
    return render(request, "inventarisation_form.html", {'page_id': page_id, 'inventarisation': inventarisation, 'group': group, 'defaults': pre_filled})


def get_cur_block(inventarisation, page_id):
    items = Item.objects.filter(location=inventarisation.location).order_by('signature')
    page_counter = 10
    current_block_clear = True

    cur_block = 0
    for item in items:
        if page_counter == 0:
            if cur_block > int(page_id) and not current_block_clear:
                return cur_block


            current_block_clear = True
            page_counter = 10
            cur_block = cur_block + 1
        page_counter -= 1
        if cur_block >= int(page_id):
            item_states = ItemState.objects.filter(inventarisation=inventarisation, item=item)
            if len(item_states) == 0:
                current_block_clear = False
    return -2


def get_inventarisation_next(request, inventarisation_id, page_id):
    inventarisation = Inventarisation.objects.get(pk=inventarisation_id)
    page_id = get_cur_block(inventarisation, page_id)
    if page_id > -2:
        return HttpResponseRedirect(reverse('inventarisation.by_number', args=(inventarisation_id, page_id)))

    page_id = get_cur_block(inventarisation, -1)
    if  page_id == -2:
        print("TO finished page")
        return HttpResponseRedirect(reverse('inventarisation.list'))
    else:
        print("Retry")
        return HttpResponseRedirect(reverse('inventarisation.list'))
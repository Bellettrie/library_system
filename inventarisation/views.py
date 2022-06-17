from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from inventarisation.models import Inventarisation
from works.models import Item, ItemState, Location


@permission_required('inventarisation.view_inventarisation')
def list_inventarisations(request):
    inventarisations = Inventarisation.objects.order_by('-is_active', '-dateTime')
    return render(request, "inventarisation/list.html", {'inventarisations': inventarisations})


def get_groups(inventarisation):
    items = Item.objects.filter(location=inventarisation.location).order_by('book_code_sortable')
    groups = []
    counter = 0

    for item in items:
        if counter == 0:
            groups.append([])
            counter = 10
        groups[len(groups) - 1].append(item)
        counter -= 1
    return groups


@permission_required('inventarisation.view_inventarisation')
def print_list(request, inventarisation_id):
    inventarisation = get_object_or_404(Inventarisation, pk=inventarisation_id)
    groups = get_groups(inventarisation)
    return render(request, "inventarisation/list_print.html", {'groups': groups})


class InventarisationCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'inventarisation.add_inventarisation'
    model = Inventarisation
    fields = ['location']
    template_name = 'inventarisation/new.html'
    success_url = reverse_lazy('inventarisation.list')


@transaction.atomic
@permission_required('inventarisation.change_inventarisation')
def inventarisation_form(request, inventarisation_id, page_id):
    inventarisation = get_object_or_404(Inventarisation, pk=inventarisation_id)
    groups = get_groups(inventarisation)
    page_id = max(0, min(len(groups) - 1, int(page_id)))

    if len(groups) == 0:
        return HttpResponseRedirect(reverse('inventarisation.finish', args=[inventarisation_id]))
    group = groups[page_id]
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
    return render(request, "inventarisation/form.html", {'page_id': page_id, 'inventarisation': inventarisation, 'group': group, 'defaults': pre_filled, "counts": len(groups)})


def get_cur_block(inventarisation, page_id):
    items = Item.objects.filter(location=inventarisation.location).order_by('book_code_sortable')
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
    if not current_block_clear and cur_block > int(page_id):
        return cur_block
    return -2


@permission_required('inventarisation.view_inventarisation')
def get_inventarisation_next(request, inventarisation_id, page_id):
    inventarisation = get_object_or_404(Inventarisation, pk=inventarisation_id)
    page_id = get_cur_block(inventarisation, page_id)
    if page_id > -2:
        return HttpResponseRedirect(reverse('inventarisation.by_number', args=(inventarisation_id, page_id)))
    page_id = get_cur_block(inventarisation, -1)
    if page_id == -2:
        return HttpResponseRedirect(reverse('inventarisation.finish', args=[inventarisation_id]))
    else:
        return HttpResponseRedirect(reverse('inventarisation.early', args=[inventarisation_id]))


@permission_required('inventarisation.view_inventarisation')
def get_inventarisation_finish(request, inventarisation_id):
    inventarisation = get_object_or_404(Inventarisation, pk=inventarisation_id)
    return render(request, "inventarisation/finish.html", {'inventarisation': inventarisation})


@transaction.atomic
@permission_required('inventarisation.change_inventarisation')
def get_inventarisation_finished(request, inventarisation_id):
    inventarisation = get_object_or_404(Inventarisation, pk=inventarisation_id)
    inventarisation.is_active = False
    inventarisation.save()
    return render(request, "inventarisation/finished.html", {'inventarisation': inventarisation})


@permission_required('inventarisation.view_inventarisation')
def get_inventarisation_early_end(request, inventarisation_id):
    inventarisation = get_object_or_404(Inventarisation, pk=inventarisation_id)
    return render(request, "inventarisation/early_end.html", {'inventarisation': inventarisation})


@transaction.atomic
@permission_required('inventarisation.add_inventarisation')
def get_inventarisation_for_all(request):
    inventarisations = []
    for location in Location.objects.all():
        inventarisations.append(Inventarisation.objects.create(location=location))
    return render(request, "inventarisation/add_for_all.html", {'inventarisations': inventarisations})

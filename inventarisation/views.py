from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from inventarisation.models import Inventarisation
from works.models import Item, ItemState, Location, available_states


@permission_required('inventarisation.view_inventarisation')
def list_inventarisations(request):
    inventarisations = Inventarisation.objects.order_by('-is_active', '-date_time')
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

    # Scoped this class here, since it should not be used elsewhere.
    class InventarisationRow:
        def __init__(self, item, state, prev_state):
            self.item = item
            self.state = state
            self.prev_state = prev_state

    inventarisation = get_object_or_404(Inventarisation, pk=inventarisation_id)
    groups = get_groups(inventarisation)
    page_id = max(0, min(len(groups) - 1, int(page_id)))

    if len(groups) == 0:
        return HttpResponseRedirect(reverse('inventarisation.finish', args=[inventarisation_id]))
    group = groups[page_id]
    if request.method == "POST":
        for z in request.POST:
            if z.startswith('seen'):
                try:
                    item_inventarisation_state = request.POST[z]  # yes, no, maybe

                    item = Item.objects.get(pk=int(z[4:]))  # what item is it?
                    current_state = item.get_state()  # what is the current state of the item?
                    prev_state = current_state  # the state after the inventarisation action is the current state

                    already_in_current_inventarisation = False  # if the current state is not part of the inventarisation, we can reuse it

                    if current_state.inventarisation == inventarisation:
                        prev_state = item.get_prev_state()  # if the current state is part of the inventarisation, we need to get the previous state
                        already_in_current_inventarisation = True  # if the current state is part of the inventarisation, we need to reuse it

                    if item_inventarisation_state == "yes" or item_inventarisation_state == "no":
                        # The item either goes to yes, or no, so we need to figure out to which state we need to move it
                        new_state, description = get_next_state_by_action(item_inventarisation_state, prev_state)
                        if already_in_current_inventarisation:
                            # If in current inventarisation, update existing line
                            current_state.type = new_state
                            current_state.reason = description
                            current_state.save()
                        else:
                            # Otherwise, we remove pre-existing lines that aren't prev, and then create a new one
                            ItemState.objects.filter(item=item, inventarisation=inventarisation).delete()
                            ItemState.objects.create(item=item, type=new_state, inventarisation=inventarisation,
                                                     reason=description)
                    else:
                        # If skip is pressed, remove all rows for this item in this
                        ItemState.objects.filter(item=item, inventarisation=inventarisation).delete()
                except Item.DoesNotExist:
                    continue

        if request.POST.get("next"):
            return get_inventarisation_next(request, inventarisation_id, page_id)

    rows = []
    for item in group:
        prev = item.get_most_recent_state_not_this_inventarisation(inventarisation)
        try:
            state_in_inventarisation = ItemState.objects.get(item=item, inventarisation=inventarisation)
            if state_in_inventarisation.type in available_states:
                rows.append(InventarisationRow(item, "yes", prev))
            else:
                rows.append(InventarisationRow(item, "no", prev))
        except ItemState.DoesNotExist:
            rows.append(InventarisationRow(item, "skip", prev))

    return render(
        request,
        "inventarisation/form.html",
        {
            'page_id': page_id,
            'inventarisation': inventarisation,
            'group': group,
            "rows": rows,
            "counts": len(groups)
        }
    )


def get_next_state_by_action(action, prev_state) -> (str, str):
    new_state = prev_state.type
    description = prev_state.reason  # By default, keep description
    if action == "yes":
        if prev_state.type == "MISSING" or prev_state.type == "LOST":
            new_state = "AVAILABLE"
            description = "Seen during inventarisation"
    elif action == "no":
        if prev_state.type == "SOLD":
            new_state = "SOLD"
        elif prev_state.type == "MISSING" or prev_state.type == "LOST":
            new_state = "LOST"
            description = "Not seen during inventarisation"
        else:
            new_state = "MISSING"
            description = "Not seen during inventarisation"
    return new_state, description


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

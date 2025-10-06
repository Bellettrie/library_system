from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from book_code_generation.helpers import normalize_str, get_number_for_str
from creators.forms import EditForm, CreatorLocationNumberFormset
from creators.models import Creator, CreatorLocationNumber, force_relabel
from creators.procedures.creator_books import get_works_for_author
from utils.get_query_words import get_query_words
from works.models import CreatorToWork


# @permission_required('creators.view_creator')
def get_authors_by_query(request, search_text):
    creators = Creator.objects.all()
    for word in search_text.split(" "):
        zz = Creator.objects.filter(Q(name__icontains=word) | Q(given_names__icontains=word))
        creators = creators & zz
    list = []
    for creator in creators:
        list.append({'id': creator.pk, 'text': creator.get_canonical_name()})
    return JsonResponse({'results': list}, safe=False)


@permission_required('creators.change_creator')
def edit(request, creator_id=None):
    creator = None
    if creator_id is not None:
        creator = get_object_or_404(Creator, pk=creator_id)
    locations = None
    location_datas = CreatorLocationNumber.objects.filter(creator=creator)
    location_dict = {}
    for i in location_datas:
        location_dict[i.location] = (i.number, i.letter)
    if request.method == 'POST':
        if creator_id is not None:
            form = EditForm(request.POST, instance=creator)
            locations = CreatorLocationNumberFormset(request.POST, instance=creator)
        else:
            form = EditForm(request.POST)
            locations = CreatorLocationNumberFormset(request.POST)
        if form.is_valid() and locations.is_valid():
            instance = form.save()
            instances = locations.save(commit=False)
            for inst in locations.deleted_objects:
                inst.delete()
            for c2w in instances:
                if c2w.location in location_dict.keys():
                    ld = location_dict[c2w.location]
                    if ld[0] != c2w.number or ld[1] != c2w.letter:
                        if request.POST.get("allow_change"):
                            force_relabel(c2w, ld[0], ld[1])
                        else:
                            form.add_error(None,
                                           "To change the location number of one of the locations, items have to be relabeled. Set the checkbox to allow this.")
                            return render(request, 'creators/edit.html',
                                          {'form': form, 'creator': creator, 'locations': locations})

                c2w.creator = instance
                c2w.save()

            return HttpResponseRedirect(reverse('creator.view', args=(instance.pk,)))
    else:
        if creator_id is not None:
            locations = CreatorLocationNumberFormset(instance=creator)
            form = EditForm(instance=creator)
        else:
            locations = CreatorLocationNumberFormset()
            form = EditForm()
    return render(request, 'creators/edit.html', {'form': form, 'creator': creator, 'locations': locations})


# @permission_required('creators.view_creator')
def show(request, creator_id):
    creator = Creator.objects.get(pk=creator_id)
    publications = get_works_for_author(creator)
    return render(request, 'creators/creator_view.html', {'creator': creator, 'publications': publications})


@permission_required('creators.delete_creator')
def delete(request, creator_id):
    creator = Creator.objects.get(pk=creator_id)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html',
                      {'what': "delete creator with name " + (creator.get_name() or "<No name> ")})
    CreatorToWork.objects.filter(creator=creator).delete()
    creator.delete()

    return redirect('creator.list')


class CreatorList(ListView):
    # permission_required = 'creators.view_creator'
    model = Creator
    template_name = 'creators/list.html'
    paginate_by = 10

    def get_queryset(self):  # new
        words = get_query_words(self.request.GET.get('q'))

        if words is None:
            return []
        if len(words) == 0:
            return []

        result_set = None
        for word in words:
            members = Creator.objects.filter(Q(name__icontains=word) | Q(given_names__icontains=word))

            if result_set is None:
                result_set = members
            else:
                result_set = result_set & members

        return list(set(result_set))


def sort_key(obj):
    def aa(obj2):
        name = normalize_str(obj.name + " " + obj.given_names)
        name2 = normalize_str(obj2.name + " " + obj2.given_names)
        if name2 > name:
            return -get_number_for_str(name2)
        else:
            return get_number_for_str(name2)

    return aa

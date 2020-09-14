from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from creators.forms import EditForm, CreatorLocationNumberFormset
from creators.models import Creator
from utils.get_query_words import get_query_words
from works.models import CreatorToWork, Publication


@permission_required('creators.view_creator')
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
    return render(request, 'creator_edit.html', {'form': form, 'creator': creator, 'locations': locations})


@permission_required('creators.view_creator')
def show(request, creator_id):
    creator = Creator.objects.get(pk=creator_id)

    works = Publication.objects.filter(creatortowork__creator=creator)

    return render(request, 'creator_view.html', {'creator': creator, 'works': works})


@permission_required('creators.delete_creator')
def delete(request, creator_id):
    creator = Creator.objects.get(pk=creator_id)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete series with name " + (creator.get_name() or "<No name> ")})
    CreatorToWork.objects.filter(creator=creator).delete()
    creator.delete()

    return redirect('creator.list')


class CreatorList(PermissionRequiredMixin, ListView):
    permission_required = 'creators.view_creator'
    model = Creator
    template_name = 'creator_list.html'
    paginate_by = 10

    def get_queryset(self):  # new
        words = get_query_words(self.request)
        get_previous = self.request.GET.get('previous', False)

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

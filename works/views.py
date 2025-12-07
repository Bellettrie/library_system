from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

from recode.procedures.update_recode import update_recode_for_item
from search.procedures.search_query.filters import AnyWordFilter, CreatorFilter, SeriesFilter, TitleFilter, BookCodeFilter, \
    CategoriesFilter, StatesFilter
from search.procedures.search_query.query_results import AllWorks, ItemsOnly, AvailableItemsOnly
from search.procedures.search_query.search_query import SearchQuery

from series.models import Graph
from utils.get_query_words import get_query_words
from utils.time import get_now
from works.forms import ItemStateCreateForm, ItemCreateForm, WorkForm, \
    LocationChangeForm
from works.forms import RelationForm, RelationFormRev, SubWorkForm
from works.models import Work, Item, ItemState, \
    Category, WorkRelation, CreatorToWork
from works.models.item_state import get_available_states
from works.procedures.orphaned_work import orphaned


def get_works(request, advanced_override=False):
    if request.GET.get('q', "").count("*") + \
            request.GET.get('q_author', "").count("*") + \
            request.GET.get('q_series', "").count("*") + \
            request.GET.get('q_title', "").count("*") + \
            request.GET.get('q_bookcode', "").count("*") > 3:
        raise ValueError("That's too much for me, senpai")
    query = SearchQuery(AllWorks())

    if request.GET.get('advanced', 'False') != 'True' and not advanced_override:
        query.set_result_base(AvailableItemsOnly())

    words = get_query_words(request.GET.get('q', "").upper())
    if len(words) > 0:
        query.add_filter(AnyWordFilter(words))

    words_author = get_query_words(request.GET.get('q_author', "").upper())
    if len(words_author) > 0:
        query.add_filter(CreatorFilter(words_author))

    words_series = get_query_words(request.GET.get('q_series', "").upper())
    if len(words_series) > 0:
        query.add_filter(SeriesFilter(words_series))

    words_title = get_query_words(request.GET.get('q_title', "").upper())
    if len(words_title) > 0:
        query.add_filter(TitleFilter(words_title))

    book_code = request.GET.get('q_bookcode', "").upper()
    if len(book_code) > 0:
        query.add_filter(BookCodeFilter(book_code))

    categories = request.GET.getlist('q_categories', [])
    if len(categories) > 0:
        query.add_filter(CategoriesFilter(words))
    states = request.GET.getlist('q_states', [])
    if len(states) > 0:
        query.add_filter(StatesFilter(words))

    return query.search()


class WorkList(ListView):
    model = Work
    template_name = 'works/publication_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        advanced = self.request.GET.get("advanced", False)
        admin = self.request.GET.get("admin", False)

        context['advanced'] = advanced
        context['admin'] = admin

        choices = ItemState.CHOICES
        choices.sort(key=lambda x: x[0])

        context['states'] = choices
        context['selected_states'] = self.request.GET.getlist("q_states", [])
        context['categories'] = Category.objects.all()
        context['selected_categories'] = list(map(lambda val: int(val), self.request.GET.getlist("q_categories", [])))

        # Add in a QuerySet of all the books
        return context

    def get_queryset(self):  # new
        return get_works(self.request)


def search_works_json(request):
    if request.GET:
        works = get_works(request, advanced_override=True)[0:50]
        lst = []
        for work in works:
            lst.append({'id': work.pk, 'text': work.get_description_title()})
        return JsonResponse({'results': lst}, safe=False)
    else:
        return JsonResponse({'results': []})


def publication_view(request, pk):
    work = get_object_or_404(Work, pk=pk)
    template_name = 'works/publication_view.html'
    series = work.as_series
    part_of_series = WorkRelation.objects.filter(from_work=work,
                                                 relation_kind__in=[WorkRelation.RelationKind.part_of_series,
                                                                    WorkRelation.RelationKind.part_of_secondary_series]).all()
    data = {
        "work": work,
        "part_of_series": part_of_series,
    }
    if series:
        data['series'] = series
        data['series_graph'] = Graph.new_from_work(work)

    return render(request, template_name, data)


def create_item_state_hx(request, item_id):
    return create_item_state(request, item_id, True)


@transaction.atomic
@permission_required('works.change_itemstate')
def create_item_state(request, item_id, hx_enabled=False):
    if request.method == 'POST':
        form = ItemStateCreateForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.item = get_object_or_404(Item, pk=item_id)
            instance.save()
            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            return HttpResponseRedirect(reverse('work.view', args=(instance.item.publication.pk,)))
    else:
        form = ItemStateCreateForm()
    return render(request, 'works/modals/item_state_edit.html',
                  {'hx_enabled': hx_enabled, 'form': form, 'item': get_object_or_404(Item, pk=item_id)})


@transaction.atomic
@permission_required('works.change_item')
def change_item_location(request, item_id, hx_enabled=False):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = LocationChangeForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            book_code = form.cleaned_data['book_code']
            book_code_extension = form.cleaned_data['book_code_extension']
            update_recode_for_item(item, book_code, book_code_extension, False)

            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            return HttpResponseRedirect(reverse('work.view', args=(item.publication.pk,)))
    else:
        form = LocationChangeForm(instance=item)
    return render(request, 'works/modals/item_location_edit.html',
                  {'hx_enabled': hx_enabled, 'form': form, 'item': item, 'item_id': item_id})


@transaction.atomic
@permission_required('works.add_item')
def item_new(request, publication_id=None):
    publication = get_object_or_404(Work, pk=publication_id)

    if request.method == 'POST':
        form = ItemCreateForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.publication = publication
            instance.save()
            return HttpResponseRedirect(reverse('work.view', args=(instance.publication.pk,)))
    else:
        form = ItemCreateForm()
    return render(request, 'works/item_edit.html', {'form': form, 'publication': publication})


@transaction.atomic
@permission_required('works.change_item')
def item_edit(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ItemCreateForm(request.POST, instance=item)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect(reverse('work.view', args=(instance.publication.pk,)))
    else:
        form = ItemCreateForm(instance=item)
    return render(request, 'works/item_edit.html',
                  {'edit': True, 'form': form, 'publication': item.publication, "item": item})


def item_history_hx(request, item_id):
    return item_history(request, item_id, True)


@transaction.atomic
@permission_required('works.view_itemstate')
def item_history(request, item_id, hx_enabled=False):
    item = get_object_or_404(Item, pk=item_id)
    templ = 'works/modals/item_state.html'

    return render(request, templ,
                  {'hx_enabled': hx_enabled, 'item': item,
                   'history': ItemState.objects.filter(item=item).order_by('-date_time')})


@transaction.atomic
@permission_required('works.change_publication')
def publication_edit(request, publication_id=None):
    from works.forms import CreatorToWorkFormSet
    creator_to_works = None
    publication = None
    if request.method == 'POST':
        if publication_id is not None:
            publication = get_object_or_404(Work, pk=publication_id)
            form = WorkForm(request.POST, instance=publication)
        else:
            form = WorkForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_translated = instance.original_language is not None
            instance.save()
            creator_to_works = CreatorToWorkFormSet(request.POST, request.FILES, instance=instance)

            if creator_to_works.is_valid():
                instances = creator_to_works.save(commit=False)
                for inst in creator_to_works.deleted_objects:
                    inst.delete()
                for c2w in instances:
                    c2w.work = instance
                    c2w.save()
            else:
                for error in creator_to_works.errors:
                    form.add_error(None, str(error))

            return HttpResponseRedirect(reverse('work.view', args=(instance.pk,)))
    else:
        publication = None
        if publication_id is not None:
            publication = get_object_or_404(Work, pk=publication_id)
            creator_to_works = CreatorToWorkFormSet(instance=publication)
            form = WorkForm(instance=publication)
        else:
            creator_to_works = CreatorToWorkFormSet()
            form = WorkForm(initial={'date_added': get_now()})
    return render(request, 'works/publication_edit.html',
                  {'publication': publication, 'form': form, 'creators': creator_to_works})


@transaction.atomic
@permission_required('works.add_publication')
def publication_new(request):
    return publication_edit(request, publication_id=None)


@transaction.atomic
@permission_required('works.change_publication')
def subwork_edit(request, subwork_id=None, publication_id=None):
    from works.forms import CreatorToWorkFormSet
    subwork_relations = []
    if subwork_id is not None:
        subwork_relations = WorkRelation.objects.filter(from_work_id=subwork_id,
                                                        relation_kind=WorkRelation.RelationKind.sub_work_of)
    if len(subwork_relations) > 0:
        subwork_relation = subwork_relations[0]
        subwork = subwork_relation.from_work

        num = subwork_relation.relation_index
        disp_num = subwork_relation.relation_index_label
    else:
        subwork_relation = None
        subwork = None
        num = 0
        disp_num = ''

    num = request.POST.get('num', num)
    disp_num = request.POST.get('disp_num', disp_num)

    if request.method == 'POST':
        form = SubWorkForm(request.POST, instance=subwork)
        if form.is_valid():
            subwork_instance = form.save(commit=False)
            subwork_instance.is_translated = subwork_instance.original_language is not None
            subwork_instance.save()
            creator_to_works = CreatorToWorkFormSet(request.POST, instance=subwork_instance)
            sub_form_has_errors = save_creator_work_relations(creator_to_works, subwork_instance)
            subwork_relation = save_subwork_relations(disp_num, subwork_instance, num, publication_id, subwork_relation)

            # Both saves went okay
            if not (sub_form_has_errors or len(form.errors) > 0):
                return HttpResponseRedirect(reverse('work.view', args=(subwork_relation.to_work_id,)))

    creator_to_works = CreatorToWorkFormSet(instance=subwork)
    form = SubWorkForm(instance=subwork)

    return render(request, 'works/subwork_edit.html',
                  {'publication': subwork_relation, 'form': form, 'creators': creator_to_works,
                   'num': num,
                   'disp_num': disp_num})


@transaction.atomic
@permission_required('works.add_publication')
def subwork_new(request, publication_id):
    return subwork_edit(request, publication_id=publication_id)


@transaction.atomic
@permission_required('works.delete_work')
def delete_work(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    if not work.is_deletable():
        return HttpResponse(status=404, content=b'Cannot delete work, still linked')
    if request.GET.get('confirm'):
        CreatorToWork.objects.filter(work=work).delete()
        work.delete()
        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return HttpResponseRedirect(request.GET.get("next"))
        return HttpResponseRedirect("/")
    return render(request, 'are-you-sure.html',
                  {
                      'what': f'delete work "{work.get_title_or_no_title()}"?',
                      'requestpath': request.path}
                  )


@transaction.atomic
@permission_required('works.delete_work')
def work_ask_delete(request, work_id, return_to=None, hx_enabled=False):
    work = get_object_or_404(Work, id=work_id)
    return render(request, 'works/work_ask_delete.html',
                  {"work": work, "return_to": return_to, "hx_enabled": hx_enabled})


@transaction.atomic
@permission_required('works.delete_workrelation')
def remove_relation(request, work_id, relation_id, hx_enabled=False):
    relation = get_object_or_404(WorkRelation, id=relation_id)
    if request.GET.get('confirm'):
        relation.delete()
        if orphaned(relation.from_work):
            return HttpResponseRedirect(reverse('work.ask_delete', args=(relation.from_work.id, relation.to_work.id)))
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        return HttpResponseRedirect(reverse('work.view', args=(work_id,)))
    return render(request, 'are-you-sure.html',
                  {
                      'what': f'delete relation "{relation.from_work.get_title_or_no_title()} {relation.relation_kind_description()} {relation.to_work.get_title_or_no_title()}"?',
                      'requestpath': request.path, 'hx_enabled': hx_enabled})


@permission_required('works.change_workrelation')
def edit_relation_to_work(request, work_id, relation_id=None, hx_enabled=False):
    if relation_id == '-1':
        relation_id = None
    relation = None
    if relation_id is not None:
        relation = get_object_or_404(WorkRelation, id=relation_id)

    work = get_object_or_404(Work, pk=work_id)
    if relation is None:
        relation = WorkRelation(from_work=work)
    if request.POST:
        form = RelationForm(request.POST, instance=relation)
        if form.is_valid():
            form.save()
            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            return HttpResponseRedirect(reverse('work.view', args=(work_id,)))
    else:
        form = RelationForm(instance=relation)

    return render(request, 'works/modals/relation_edit.html',
                  {'form': form, 'hx_enabled': hx_enabled, 'work': work, "fwd": True})


@permission_required('works.change_workrelation')
def edit_relation_from_work(request, work_id, relation_id=None, hx_enabled=False):
    if relation_id == '-1':
        relation_id = None
    relation = None
    if relation_id is not None:
        relation = get_object_or_404(WorkRelation, id=relation_id)

    work = get_object_or_404(Work, pk=work_id)
    if relation is None:
        relation = WorkRelation(to_work=work)
    if request.POST:
        form = RelationFormRev(request.POST, instance=relation)
        if form.is_valid():
            form.save()
            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            return HttpResponseRedirect(reverse('work.view', args=(work_id,)))
    else:
        form = RelationFormRev(instance=relation)

    return render(request, 'works/modals/relation_edit.html',
                  {'form': form, 'hx_enabled': hx_enabled, 'work': work, "fwd": False})


def save_subwork_relations(disp_num, instance, num, publication_id, subwork_relation):
    if subwork_relation is None:
        publication = get_object_or_404(Work, pk=publication_id)

        subwork_relation = WorkRelation.objects.create(from_work=instance, to_work=publication,
                                                       relation_index=num,
                                                       relation_index_label=disp_num,
                                                       relation_kind=WorkRelation.RelationKind.sub_work_of)
    else:
        subwork_relation.relation_index = num
        subwork_relation.relation_index_label = disp_num
        subwork_relation.save()
    return subwork_relation


def save_creator_work_relations(creator_to_works, work):
    sub_form_has_errors = False
    if creator_to_works.is_valid():
        instances = creator_to_works.save(commit=False)
        for inst in creator_to_works.deleted_objects:
            inst.delete()
        for c2w in instances:
            c2w.work = work
            c2w.save()
    else:
        if len(creator_to_works.errors) > 0:
            sub_form_has_errors = True
    return sub_form_has_errors

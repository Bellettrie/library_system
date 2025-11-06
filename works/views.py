from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models.expressions import RawSQL, F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView, ListView

from recode.models import Recode
from recode.procedures.update_recode import update_recode_for_item
from search.queries import filter_state, filter_book_code_get_q, \
    filter_basic_text_get_q, filter_author_text, filter_series_text, filter_title_text, filter_location, \
    filter_basic_text
from utils.get_query_words import get_query_words
from works.forms import ItemStateCreateForm, ItemCreateForm, PublicationCreateForm, SubWorkCreateForm, \
    LocationChangeForm
from works.models import Work, Item, ItemState, WorkInPublication, \
    Category


def get_works(request):
    if request.GET.get('q', "").count("*") + \
            request.GET.get('q_author', "").count("*") + \
            request.GET.get('q_series', "").count("*") + \
            request.GET.get('q_title', "").count("*") + \
            request.GET.get('q_bookcode', "").count("*") > 3:
        raise ValueError("That's too much for me, senpai")

    words = get_query_words(request.GET.get('q', "").upper())
    words_author = get_query_words(request.GET.get('q_author', "").upper())
    words_series = get_query_words(request.GET.get('q_series', "").upper())
    words_title = get_query_words(request.GET.get('q_title', "").upper())
    book_code = request.GET.get('q_bookcode', "").upper()
    categories = request.GET.getlist('q_categories', [])
    states = request.GET.getlist('q_states', [])

    query = Work.objects
    query = query_annotate_and_sort_bookcodes(query)
    any_query = False
    # If one word, also check bookcodes
    if len(words) == 1:
        any_query = True
        fbc = filter_book_code_get_q(words[0])
        fbt = filter_basic_text_get_q(words)[0]
        query = query.filter(fbc | fbt)
    elif len(words) > 1:
        any_query = True

        query = filter_basic_text(query, words)

    if len(words_author) > 0:
        any_query = True
        query = filter_author_text(query, words_author)
    if len(words_series) > 0:
        any_query = True
        query = filter_series_text(query, words_series)
    if len(words_title) > 0:
        any_query = True
        query = filter_title_text(query, words_title)

    if len(categories) > 0:
        any_query = True
        query = filter_location(query, categories)
    if len(book_code) > 0:
        any_query = True
        query = query.filter(filter_book_code_get_q(book_code))
    if len(states) > 0:
        any_query = True
        query = filter_state(query, states)

    if not any_query:
        return Work.objects.none()
    return query


def query_annotate_and_sort_bookcodes(query):
    query = query.annotate(
        itemid=F('item__id'),
        book_code_sortable=F('item__book_code_sortable'),
        book_code=F('item__book_code'),
        book_code_extension=F('item__book_code_extension')
    )
    query = query.order_by("book_code_sortable", "id", 'itemid')
    query = query.distinct("book_code_sortable", "id", 'itemid')
    return query


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


class WorkDetail(DetailView):
    template_name = 'works/publication_view.html'
    model = Work


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
    from works.forms import SeriesToWorkFomSet
    creator_to_works = None
    series_to_works = None
    publication = None
    if request.method == 'POST':
        if publication_id is not None:
            publication = get_object_or_404(Work, pk=publication_id)
            form = PublicationCreateForm(request.POST, instance=publication)
        else:
            form = PublicationCreateForm(request.POST)
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

            series_to_works = SeriesToWorkFomSet(request.POST, request.FILES, instance=instance)

            if series_to_works.is_valid():
                instances = series_to_works.save(commit=False)
                for inst in series_to_works.deleted_objects:
                    inst.delete()
                for i in instances:
                    i.work = instance
                    i.save()
            else:
                for error in series_to_works.errors:
                    form.add_error(None, str(error))
            return HttpResponseRedirect(reverse('work.view', args=(instance.pk,)))
    else:
        publication = None
        if publication_id is not None:
            publication = get_object_or_404(Work, pk=publication_id)
            creator_to_works = CreatorToWorkFormSet(instance=publication)
            series_to_works = SeriesToWorkFomSet(instance=publication)
            form = PublicationCreateForm(instance=publication)
        else:
            creator_to_works = CreatorToWorkFormSet()
            series_to_works = SeriesToWorkFomSet()
            form = PublicationCreateForm()
    return render(request, 'works/publication_edit.html',
                  {'series': series_to_works, 'publication': publication, 'form': form, 'creators': creator_to_works})


@transaction.atomic
@permission_required('works.add_publication')
def publication_new(request):
    return publication_edit(request, publication_id=None)


@transaction.atomic
@permission_required('works.change_publication')
def subwork_edit(request, subwork_id=None, publication_id=None):
    from works.forms import CreatorToWorkFormSet
    creator_to_works = None
    series = None
    publication = None
    num = 0
    disp_num = ''
    if request.method == 'POST':

        if subwork_id is not None:
            publication = get_object_or_404(WorkInPublication, pk=subwork_id)
            num = publication.number_in_publication
            disp_num = publication.display_number_in_publication
            form = SubWorkCreateForm(request.POST, instance=publication.work)
        else:
            form = SubWorkCreateForm(request.POST)
        num = request.POST.get('num', num)
        disp_num = request.POST.get('disp_num', disp_num)
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

            if subwork_id is None:
                pub = get_object_or_404(Work, id=publication_id)
                publication = WorkInPublication.objects.create(work=instance, publication=pub,
                                                               number_in_publication=num,
                                                               display_number_in_publication=disp_num)
            else:
                publication.number_in_publication = num
                publication.display_number_in_publication = disp_num
                publication.save()

            return HttpResponseRedirect(reverse('work.view', args=(publication.publication_id,)))
    else:
        if subwork_id is not None:
            publication = get_object_or_404(WorkInPublication, pk=subwork_id)
            num = publication.number_in_publication
            disp_num = publication.display_number_in_publication
            creator_to_works = CreatorToWorkFormSet(instance=publication.work)
            form = SubWorkCreateForm(instance=publication.work)
        else:
            creator_to_works = CreatorToWorkFormSet()
            form = SubWorkCreateForm()
    return render(request, 'works/subwork_edit.html',
                  {'series': series, 'publication': publication, 'form': form, 'creators': creator_to_works, 'num': num,
                   'disp_num': disp_num})


@transaction.atomic
@permission_required('works.add_publication')
def subwork_new(request, publication_id):
    return subwork_edit(request, publication_id=publication_id)


@transaction.atomic
@permission_required('works.add_publication')
def subwork_delete(request, subwork_id):
    publication = get_object_or_404(WorkInPublication, pk=subwork_id)

    if request.GET.get('confirm'):
        work = publication.work
        publication.delete()
        work.delete()
        return HttpResponseRedirect(reverse('work.view', args=(publication.publication_id,)))
    return render(request, 'are-you-sure.html', {'what': 'delete the subwork ' + publication.work.get_title() + "?"})

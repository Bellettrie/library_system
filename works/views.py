import re

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView, ListView

from lendings.models import Lending
from recode.models import Recode


from utils.get_query_words import get_query_words
from works.forms import ItemStateCreateForm, ItemCreateForm, PublicationCreateForm, SubWorkCreateForm
from works.models import Work, Publication, Item, ItemState, WorkInPublication, \
    Category


def word_to_regex(word: str):
    if re.match('^[\\w-]+?$', word.replace("*", "").replace("+", "").replace("?", "")) is None:
        return ""
    word = word.replace("*", ".*")
    word = word.replace("?", ".?")
    word = word.replace("+", ".+")
    return "(?<!\\S)" + word + "(?!\\S)"


def sort_works(work: Work):
    return work.old_id


def sorter(dictt):
    return lambda a: -dictt[a]


def merge_queries(query, add_query):
    if query is None:
        return add_query
    else:
        return AndOp(query, add_query)


def get_works_for_publication(words_for_q, words_for_author=[], words_for_series=[], words_for_title=[], states=[],
                              categories=[], book_code=""):
    query = None
    if len(words_for_q) > 0:
        query = merge_queries(query, BaseSearchQuery(" ".join(words_for_q)))
    if len(words_for_author) > 0:
        query = merge_queries(query, AuthorSearchQuery(" ".join(words_for_author)))
    if len(words_for_series) > 0:
        query = merge_queries(query, SeriesSearchQuery(" ".join(words_for_series)))
    if len(words_for_title) > 0:
        query = merge_queries(query, TitleSearchQuery(" ".join(words_for_title)))

    if len(categories) > 0:
        query = merge_queries(query, LocationSearchQuery(categories))
    if len(book_code) > 0:
        query = merge_queries(query, BookCodeSearchQuery(book_code))
    inbetween_list = []
    if query is not None:
        result_set = query.exec()
        inbetween_list = list(set(result_set))
    work_list = []
    if len(states) > 0:
        in_right_state_ones = set(search_state(states))
        if query is None:
            work_list = list(in_right_state_ones)
        if len(in_right_state_ones) == 0:
            work_list = inbetween_list
        else:
            for w in inbetween_list:
                if w in in_right_state_ones:
                    work_list.append(w)
    else:
        work_list = inbetween_list

    work_list.sort(key=lambda a: (a.title or "").upper())
    work_list.sort(key=lambda a: a.listed_author)
    return work_list


def get_works_by_book_code(word):
    word = word_to_regex(word)
    if len(word) == 0:
        return []
    items = Item.objects.filter(Q(book_code__iregex=word) | Q(book_code_sortable__iregex=word)).prefetch_related(
        "publication")
    results = []
    for item in items:
        results.append(item.publication)
    return results


def get_works(request):
    if request.GET.get('q', "").count("*") + \
            request.GET.get('q_author', "").count("*") + \
            request.GET.get('q_series', "").count("*") + \
            request.GET.get('q_title', "").count("*") + \
            request.GET.get('q_bookcode', "").count("*") > 3:
        raise ValueError("That's too much for me, senpai")

    words = get_query_words(request.GET.get('q', ""))
    words_author = get_query_words(request.GET.get('q_author', ""))
    words_series = get_query_words(request.GET.get('q_series', ""))
    words_title = get_query_words(request.GET.get('q_title', ""))
    book_code = request.GET.get('q_bookcode', "")

    states = request.GET.getlist('q_states', [])
    categories = request.GET.getlist('q_categories', [])

    results = []
    if len(words) == 1 and not request.GET.get('advanced', False):
        results += get_works_by_book_code(words[0])
    results += get_works_for_publication(words, words_author, words_series, words_title, states, categories, book_code)
    return results


class WorkList(ListView):
    model = Work
    template_name = 'works/publication_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        advanced = self.request.GET.get("advanced", False)
        context['advanced'] = advanced

        context['states'] = ItemState.CHOICES
        context['selected_states'] = self.request.GET.getlist("q_states", [])
        context['categories'] = Category.objects.all()
        context['selected_categories'] = list(map(lambda val: int(val), self.request.GET.getlist("q_categories", [])))

        # Add in a QuerySet of all the books
        return context

    def get_queryset(self):  # new
        result = get_works(self.request)
        return result


class WorkDetail(DetailView):
    template_name = 'works/publication_view.html'
    model = Publication


def create_item_state_hx(request, item_id):
    return create_item_state(request, item_id, True)


@transaction.atomic
@permission_required('works.change_item')
def create_item_state(request, item_id, hx_enabled=False):
    templ = 'works/item_state_edit.html'
    if hx_enabled:
        templ = 'works/item_state_edit_hx.html'

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

    return render(request, templ, {'form': form, 'item': get_object_or_404(Item, pk=item_id)})


@transaction.atomic
@permission_required('works.add_item')
def item_new(request, publication_id=None):
    publication = get_object_or_404(Publication, pk=publication_id)

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
    recode_book_code = ''
    recode_book_code_extension = ''
    recode = False
    recodes = Recode.objects.filter(item=item)
    if len(recodes) == 1:
        recode_obj = recodes[0]
        recode_book_code = recode_obj.book_code
        recode_book_code_extension = recode_obj.book_code_extension
        recode = True
    if request.method == 'POST':
        form = ItemCreateForm(request.POST, instance=item)
        recode = request.POST.get('recode_check')
        recode_book_code = request.POST.get('recode_book_code')
        recode_book_code_extension = request.POST.get('recode_book_code_extension')
        if form.is_valid():
            instance = form.save(commit=False)

            instance.save()
            recodes = Recode.objects.filter(item=item)
            for rr in recodes:
                rr.delete()
            if recode:
                Recode.objects.create(item=instance, book_code=recode_book_code,
                                      book_code_extension=recode_book_code_extension)

            return HttpResponseRedirect(reverse('work.view', args=(instance.publication.pk,)))
    else:
        form = ItemCreateForm(instance=item)
    return render(request, 'works/item_edit.html',
                  {'edit': True, 'form': form, 'publication': item.publication, 'edit': True, 'recode': recode,
                   'recode_book_code': recode_book_code,
                   'recode_book_code_extension': recode_book_code_extension})


def item_history_hx(request, item_id):
    return item_history(request, item_id, True)


@transaction.atomic
@permission_required('works.change_item')
def item_history(request, item_id, hx_enabled=False):
    item = get_object_or_404(Item, pk=item_id)
    templ = 'works/item_state.html'
    if hx_enabled:
        templ = 'works/item_state_hx.html'
    return render(request, templ,
                  {'item': item,
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
            publication = get_object_or_404(Publication, pk=publication_id)
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
            publication = get_object_or_404(Publication, pk=publication_id)
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
    from works.forms import SeriesToWorkFomSet
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
                pub = get_object_or_404(Publication, id=publication_id)
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

import re
from typing import List

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView, ListView, CreateView

from book_code_generation.models import standardize_code
from recode.models import Recode
from series.models import Series
from utils.get_query_words import get_query_words
from works.forms import ItemStateCreateForm, ItemCreateForm, PublicationCreateForm, SubWorkCreateForm
from works.models import Work, Publication, Creator, SubWork, CreatorToWork, Item, ItemState, WorkInPublication


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


class ItemRow:
    def __init__(self, item: Item, book_result=None, options=[], extra_info=None):
        self.item = item
        self.book_result = book_result
        self.options = options
        self.extra_info = extra_info

    def __str__(self):
        return self.item.book_code + self.item.book_code_extension


class BookResult:
    def __init__(self, publication: Publication, item_rows: List[ItemRow], item_options=[], publication_options=[]):
        self.publication = publication
        self.item_rows = item_rows
        self.item_options = item_options
        self.publication_options = publication_options
        self.score = 0
        for row in self.item_rows:
            row.options = item_options
            row.book_result = self

    def set_item_options(self, item_options):
        for row in self.item_rows:
            row.options = item_options


def get_works_for_publication(words):
    result_set = None
    for word in words:
        word = word_to_regex(word)
        if len(word) == 0:
            return []
        authors = Creator.objects.filter(Q(name__iregex=word) | Q(given_names__iregex=word))

        series = set(Series.objects.filter(Q(creatortoseries__creator__in=authors)
                                           | Q(title__iregex=word)
                                           | Q(sub_title__iregex=word)
                                           | Q(original_title__iregex=word)
                                           | Q(original_subtitle__iregex=word)
                                           ))

        prev_len = 0
        series_len = len(series)

        while prev_len < series_len:
            prev_len = series_len
            series = set(series | set(Series.objects.filter(part_of_series__in=series)))
            series_len = len(series)
        work_q = Q(Q(title__iregex=word)
                   | Q(sub_title__iregex=word)
                   | Q(original_title__iregex=word)
                   | Q(original_subtitle__iregex=word)
                   | Q(workinseries__part_of_series__in=series))

        subworks = set(SubWork.objects.filter(
            Q(creatortowork__creator__in=authors)
            | work_q))

        word_set = set(Publication.objects.filter(
            work_q
            | Q(workinpublication__work__in=subworks)))
        res2 = set(Publication.objects.filter(creatortowork__creator__in=authors))
        word_set = word_set | res2
        if result_set is None:
            result_set = word_set
        else:
            result_set = result_set & word_set
    work_list = list(set(result_set))
    work_list.sort(key=lambda a: a.listed_author)

    result = []
    for row in work_list:
        item_rows = []
        for item in row.item_set.all():
            item_rows.append(ItemRow(item, []))
        result.append(BookResult(row, item_rows))
    return result


def get_works_by_book_code(word):
    results = []
    pub_dict = dict()
    word = word_to_regex(word)
    if len(word) == 0:
        return []
    items = Item.objects.filter(Q(book_code__iregex=word) | Q(book_code_sortable__iregex=word))
    for item in items:
        dz = pub_dict.get(item.publication, [])
        dz.append(ItemRow(item, []))
        pub_dict[item.publication] = dz
    for key in pub_dict.keys():
        results.append(BookResult(key, pub_dict[key]))
    return results


def get_works(request):
    words = get_query_words(request)
    if words is None or words == []:
        return []

    results = []
    if len(words) == 1:
        results += get_works_by_book_code(words[0])
    results += get_works_for_publication(words)
    return results


class WorkList(ListView):
    model = Work
    template_name = 'work_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        return context

    def get_queryset(self):  # new
        result = get_works(self.request)
        for row in result:
            row.set_item_options(["lend", "reserve"])
            row.publication_options = ["edit"]
        return result


class WorkDetail(DetailView):
    template_name = 'work_detail.html'
    model = Publication


@transaction.atomic
@permission_required('works.change_item')
def create_item_state(request, item_id):
    if request.method == 'POST':
        form = ItemStateCreateForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.item = get_object_or_404(Item, pk=item_id)
            instance.save()
            return HttpResponseRedirect(reverse('work.view', args=(instance.item.publication.pk,)))
    else:
        form = ItemStateCreateForm()
    return render(request, 'item_reason_edit.html', {'form': form, 'member': get_object_or_404(Item, pk=item_id)})


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
    return render(request, 'item_edit.html', {'form': form, 'publication': publication})


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
                Recode.objects.create(item=instance, book_code=recode_book_code, book_code_extension=recode_book_code_extension)

            return HttpResponseRedirect(reverse('work.view', args=(instance.publication.pk,)))
    else:
        form = ItemCreateForm(instance=item)
    return render(request, 'item_edit.html',
                  {'edit': True, 'form': form, 'publication': item.publication, 'edit': True, 'recode': recode, 'recode_book_code': recode_book_code,
                   'recode_book_code_extension': recode_book_code_extension})


@transaction.atomic
@permission_required('works.change_item')
def item_history(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'item_history.html',
                  {'item': item,
                   'history': ItemState.objects.filter(item=item).order_by('-dateTime')})


@transaction.atomic
@permission_required('works.change_publication')
def publication_edit(request, publication_id=None):
    from works.forms import CreatorToWorkFormSet
    from works.forms import SeriesToWorkFomSet
    creators = None
    series = None
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
            creators = CreatorToWorkFormSet(request.POST, request.FILES, instance=instance)

            if creators.is_valid():
                instances = creators.save(commit=False)
                for inst in creators.deleted_objects:
                    inst.delete()
                for c2w in instances:
                    c2w.work = instance
                    c2w.save()
            else:
                for error in creators.errors:
                    form.add_error(None, str(error))

            series = SeriesToWorkFomSet(request.POST, request.FILES, instance=instance)

            if series.is_valid():
                instances = series.save(commit=False)
                for inst in series.deleted_objects:
                    inst.delete()
                for i in instances:
                    i.work = instance
                    i.save()
            else:
                for error in series.errors:
                    form.add_error(None, str(error))
            return HttpResponseRedirect(reverse('work.view', args=(instance.pk,)))
    else:
        publication = None
        if publication_id is not None:
            publication = get_object_or_404(Publication, pk=publication_id)
            creators = CreatorToWorkFormSet(instance=publication)
            series = SeriesToWorkFomSet(instance=publication)
            form = PublicationCreateForm(instance=publication)
        else:
            creators = CreatorToWorkFormSet()
            series = SeriesToWorkFomSet()
            form = PublicationCreateForm()
    return render(request, 'publication_edit.html',
                  {'series': series, 'publication': publication, 'form': form, 'creators': creators})


@transaction.atomic
@permission_required('works.add_publication')
def publication_new(request):
    return publication_edit(request, publication_id=None)


@transaction.atomic
@permission_required('works.change_publication')
def subwork_edit(request, subwork_id=None, publication_id=None):
    from works.forms import CreatorToWorkFormSet
    from works.forms import SeriesToWorkFomSet
    creators = None
    series = None
    publication = None
    num = 0
    disp_num = ''
    if request.method == 'POST':
        print(request.POST)

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
            creators = CreatorToWorkFormSet(request.POST, request.FILES, instance=instance)
            if creators.is_valid():
                instances = creators.save(commit=False)
                for inst in creators.deleted_objects:
                    inst.delete()
                for c2w in instances:
                    c2w.work = instance
                    c2w.save()
            else:
                for error in creators.errors:
                    form.add_error(None, str(error))

            if subwork_id is None:
                pub = get_object_or_404(Publication, id=publication_id)
                publication = WorkInPublication.objects.create(work=instance, publication=pub, number_in_publication=num, display_number_in_publication=disp_num)
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
            creators = CreatorToWorkFormSet(instance=publication.work)
            form = SubWorkCreateForm(instance=publication.work)
        else:
            creators = CreatorToWorkFormSet()
            form = SubWorkCreateForm()
    return render(request, 'subwork_edit.html',
                  {'series': series, 'publication': publication, 'form': form, 'creators': creators, 'num': num, 'disp_num': disp_num})


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

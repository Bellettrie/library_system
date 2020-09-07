import markdown
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.forms import Widget
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template import loader
from django.template.loader import get_template
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from public_pages.django_markdown import DjangoUrlExtension
from public_pages.forms import PageEditForm, UploadFileForm
from public_pages.models import PublicPageGroup, PublicPage, FileUpload


def render_md(markdown_text: str):
    md = markdown.Markdown(extensions=[DjangoUrlExtension(), 'tables'])
    search_template = get_template('work_search_field_simple.html')
    html = md.convert(markdown_text).replace("----SEARCH----", search_template.render(context={}))
    return html


def view_named_page(request, page_name, sub_page_name):
    print(page_name)
    page_group = get_object_or_404(PublicPageGroup, name=page_name)

    can_edit = False
    if not request.user.is_anonymous and (request.user and  ( hasattr(request.user, 'member') and page_group.committees in request.user.member.committees.all())) or request.user.has_perm('public_pages.change_publicpage'):
        can_edit = True
    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)
    html = render_md(page.text)

    return HttpResponse(render(request, template_name='public_page_simple.html',
                               context={'BASE_URL': settings.BASE_URL, 'markdown': page.text, 'page_title': page.title, 'page_content': html, 'can_edit': can_edit, 'page': page}))


def view_page(page_name, sub_page_name):
    def func(request):
        return view_named_page(request, page_name, sub_page_name)

    return func


@login_required
@csrf_exempt
def render_page_from_request(request):
    return HttpResponse(render_md(request.POST["text"]))


@login_required
def test_render_function(request):
    return HttpResponse(render(request, template_name='page_edit.html', context={}))


@login_required
@transaction.atomic
def edit_named_page(request, page_name, sub_page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)
    can_edit = False
    if not request.user.is_anonymous and (request.user.member and page_group.committees in request.user.member.committees.all()) or request.user.has_perm('public_pages.change_publicpage'):
        can_edit = True
    if not can_edit:
        return HttpResponse("cannot edit")

    if request.method == 'POST':
        form = PageEditForm(request.POST, instance=page)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('named_page', args=(page_name, sub_page_name)))
        else:
            print("ERROR")
    else:
        form = PageEditForm(instance=page)
    return render(request, 'page_edit_form.html', {'MY_URL': settings.BASE_URL, 'form': form, 'page': page})


@login_required()
@transaction.atomic
def new_named_page(request, page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    can_edit = False
    if not request.user.is_anonymous and (request.user.member and page_group.committees in request.user.member.committees.all()) or request.user.has_perm('public_pages.change_publicpage'):
        can_edit = True
    if not can_edit:
        return HttpResponse("cannot edit")
    if request.method == 'POST':
        form = PageEditForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect(reverse('named_page', args=(instance.group.name, instance.name)))
        else:
            print("ERROR")
    else:
        instance = PublicPage(group=page_group)
        form = PageEditForm(instance=instance)
    return render(request, 'page_edit_form.html', {'MY_URL': settings.BASE_URL, 'form': form})


@permission_required('public_pages.view_publicpage')
def list_named_pages(request):
    pages = PublicPage.objects.all()
    return render(request, 'page_list.html', {'MY_URL': settings.BASE_URL, 'pages': pages, 'groups': PublicPageGroup.objects.all()})


@permission_required('public_pages.delete_publicpage')
@transaction.atomic
def delete_page(request, pk):
    page = PublicPage.objects.filter(pk=pk)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete page with name " + page.first().name})

    page.delete()

    return redirect('list_pages')


def list_uploads(request):
    uploads = FileUpload.objects.all()
    return render(request, 'uploads_list.html', {'uploads': uploads})


@permission_required('public_pages.change_publicpage')
def new_upload(request):
    special = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            special = "Succesful upload!"
            form = UploadFileForm()
    else:
        form = UploadFileForm()

    return render(request, 'upload_form.html', {"form": form, "special": special})


@permission_required('public_pages.change_publicpage')
def delete_upload(request, pk):
    page = FileUpload.objects.filter(pk=pk)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete attachment with name " + page.first().name})
    page.delete()

    return redirect('list_uploads')

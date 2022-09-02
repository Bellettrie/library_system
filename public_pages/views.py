import json

import markdown
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.forms import Widget
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template import loader
from django.template.loader import get_template
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from public_pages.django_markdown import DjangoUrlExtension
from public_pages.forms import PageEditForm, UploadFileForm
from public_pages.models import PublicPageGroup, PublicPage, FileUpload, ExternalUpload


def render_md(markdown_text: str):
    md = markdown.Markdown(extensions=[DjangoUrlExtension(), 'tables', 'md_in_html'])
    search_template = get_template('works/work_search_field_simple.html')
    open_template = get_template('public_pages/is_open_template.html')
    html = md.convert(markdown_text).replace("----SEARCH----", search_template.render(context={}))
    if "----OPEN----" in html:
        import urllib.request
        f = urllib.request.urlopen(settings.IS_OPEN_URL, timeout=120)
        is_open_result = str(f.read()).lower()
        zz = open_template.render(
            context={'open': "true" in is_open_result})
        html = html.replace("----OPEN----", zz)
    return html


def view_named_page(request, page_name, sub_page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)

    can_edit = False

    if not request.user.is_anonymous and (request.user
                                          and (hasattr(request.user, 'member')
                                               and page_group.committees in request.user.member.committees.all())) \
            or request.user.has_perm('public_pages.change_publicpage'):
        can_edit = True
    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)
    html = render_md(page.text)

    return HttpResponse(render(request, template_name='public_pages/public_page_simple.html',
                               context={'BASE_URL': settings.BASE_URL, 'markdown': page.text, 'page_title': page.title,
                                        'page_content': html, 'can_edit': can_edit, 'page': page}))


def view_page(page_name: str, sub_page_name: str):
    def view_function(request: HttpRequest):
        return view_named_page(request, page_name, sub_page_name)

    return view_function


@login_required
@csrf_exempt
def render_page_from_request(request):
    return HttpResponse(render_md(request.POST["text"]))


@login_required
def test_render_function(request):
    return HttpResponse(render(request, template_name='public_pages/page_edit.html', context={}))


@login_required
@transaction.atomic
def edit_named_page(request, page_name, sub_page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)
    can_edit = False
    if not request.user.is_anonymous and (
            request.user.member and page_group.committees in request.user.member.committees.all()) \
            or request.user.has_perm('public_pages.change_publicpage'):
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
    return render(request, 'public_pages/page_edit_form.html',
                  {'MY_URL': settings.BASE_URL, 'form': form, 'page': page})


@login_required()
@transaction.atomic
def new_named_page(request, page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    can_edit = False
    if not request.user.is_anonymous and (
            request.user.member and page_group.committees in request.user.member.committees.all()) \
            or request.user.has_perm('public_pages.change_publicpage'):
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
    return render(request, 'public_pages/page_edit_form.html', {'MY_URL': settings.BASE_URL, 'form': form})


@permission_required('public_pages.view_publicpage')
def list_named_pages(request):
    pages = PublicPage.objects.all()
    return render(request, 'public_pages/page_list.html',
                  {'MY_URL': settings.BASE_URL, 'pages': pages, 'groups': PublicPageGroup.objects.all()})


@permission_required('public_pages.delete_publicpage')
@transaction.atomic
def delete_page(request, pk):
    page = PublicPage.objects.filter(pk=pk)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete page with name " + page.first().name})

    page.delete()

    return redirect('list_pages')


def list_uploads(request):
    if not settings.EXTERNAL_UPLOAD_ENABLED:
        uploads = FileUpload.objects.all()
        return render(request, 'public_pages/uploads_list.html', {'uploads': uploads})
    else:
        uploads = ExternalUpload.objects.all()
        return render(request, 'public_pages/uploads_list.html', {'uploads': uploads})


@permission_required('public_pages.change_publicpage')
def new_upload(request):
    special = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            if not settings.EXTERNAL_UPLOAD_ENABLED:
                instance.save()
                special = "Succesful upload!"
            else:
                import requests
                url = settings.EXTERNAL_UPLOAD_URL_UPLOAD
                files = {}
                for file in request.FILES:
                    files[file] = request.FILES[file]
                r = requests.post(url + "?token=" + settings.EXTERNAL_UPLOAD_URL_API_KEY, files=files)
                tx = json.loads(r.text)
                for file in files:
                    nm = tx.get("Files").get(files[file].name)
                    if not nm:
                        print("File skipped")
                        continue
                    ExternalUpload.objects.create(external_name=nm, name=instance.name)
            form = UploadFileForm()
    else:
        form = UploadFileForm()

    return render(request, 'public_pages/upload_form.html', {"form": form, "special": special})


@permission_required('public_pages.change_publicpage')
def delete_upload(request, pk):
    if not settings.EXTERNAL_UPLOAD_ENABLED:
        page = FileUpload.objects.filter(pk=pk)
        if not request.GET.get('confirm'):
            return render(request, 'are-you-sure.html', {'what': "delete attachment with name " + page.first().name})
        page.delete()

        return redirect('list_uploads')
    else:
        page = ExternalUpload.objects.filter(pk=pk)
        if not request.GET.get('confirm'):
            return render(request, 'are-you-sure.html', {'what': "Delete attachment with name " + page.first().name})
        import requests
        url = settings.EXTERNAL_UPLOAD_URL_DELETE
        for file in page.all():
            print(url + "?token=" + settings.EXTERNAL_UPLOAD_URL_API_KEY + "&files=" + file.external_name)
            r = requests.post(url + "?token=" + settings.EXTERNAL_UPLOAD_URL_API_KEY + "&files=" + file.external_name)
            print(r.text)
            file.delete()

        return redirect('list_uploads')

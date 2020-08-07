import markdown
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import Widget
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.template import loader
from django.template.loader import get_template
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from public_pages.django_markdown import DjangoUrlExtension, get_site_domain
from public_pages.forms import PageEditForm
from public_pages.models import PublicPageGroup, PublicPage


def render_md(markdown_text: str):
    md = markdown.Markdown(extensions=[DjangoUrlExtension()])
    search_template = get_template('work_search_field_simple.html')
    html = md.convert(markdown_text).replace("----SEARCH----", search_template.render(context={}))
    return html


def view_named_page(request, page_name, sub_page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    can_edit = False
    if not request.user.is_anonymous and (request.user.member and page_group.committees in request.user.member.committees.all()) or request.user.has_perm('public_pages.change_public_page'):
        can_edit = True
    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)

    html = render_md(page.text)
    print(page.name)
    print(page.group.name)
    return HttpResponse(render(request, template_name='public_page_simple.html', context={'BASE_URL': settings.BASE_URL, 'markdown': page.text, 'page_title': page.title, 'page_content': html, 'can_edit' : can_edit, 'page': page}))


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
def edit_named_page(request, page_name, sub_page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)

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

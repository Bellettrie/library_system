import markdown
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.template.loader import get_template

from public_pages.django_markdown import DjangoUrlExtension, get_site_domain
from public_pages.models import PublicPageGroup, PublicPage


def render_md(markdown_text: str):
    md = markdown.Markdown(extensions=[DjangoUrlExtension()])
    search_template = get_template('work_search_field_simple.html')
    html = md.convert(markdown_text).replace("----SEARCH----", search_template.render(context={}))
    return html


def view_named_page(request, page_name, sub_page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    print(sub_page_name)
    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)

    html = render_md(page.text)
    return HttpResponse(render(request, template_name='public_page_simple.html', context={'page_title': page.title, 'page_content': html}))


def view_page(page_name, sub_page_name):
    def func(request):
        return view_named_page(request, page_name, sub_page_name)
    return func


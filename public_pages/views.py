import markdown
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template.loader import get_template

from public_pages.django_markdown import DjangoUrlExtension, get_site_domain


def render_md(markdown_text: str):
    md = markdown.Markdown(extensions=[DjangoUrlExtension()])
    search_template = get_template('work_search_field_simple.html')
    html = md.convert(markdown_text).replace("----SEARCH----", search_template.render(context={}))
    return html


def view_page(page_name, sub_page_name):
    def func(request):
        html = render_md("""
![Drag Racing](https://miro.medium.com/proxy/1*YgtCXuRGmPfPg2PogXVCfQ.png)
[Search](lendings.list)
# hoi
## Test2 
    1. a
    # Search for books
    ----SEARCH----
    2. b
    3. c
    test
            """)
        return HttpResponse(render(request, template_name='public_page_simple.html', context={'page_title': 'title', 'page_content': html}))

    return func

import logging

import markdown
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template.loader import get_template
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from members.models import Member
from public_pages.django_markdown import DjangoUrlExtension, ProcessorExtension
from public_pages.forms import PageEditForm, UploadFileForm, PageAccessForm, EditForm
from public_pages.models import PublicPageGroup, PublicPage, FileUpload


# These functions are responsible for displaying parts of the webpages. These translate quite directly into bootstrap components
# The *_ is used to "eat" any unneeded parameters


# The interrupt ends a bootstrap row component and starts a new one.
def render_interrupt(markdown_text: str, title: str, layout_overrides: str = "", *_):
    search_template = get_template('public_pages/elems/interrupt.html')
    return search_template.render(context={"content": markdown_text})


# Shows the youtube vid
def render_yt(markdown_text: str, title: str, layout_overrides: str = "", *_):
    yt_template = get_template('public_pages/elems/yt.html')
    return yt_template.render(context={"url": markdown_text})


# The base section creates a basic text area with a size. Observe that the title parameter is ignored, but it's kept to keep standardised functions.
def render_base_section(markdown_text: str, title: str, layout_overrides: str = "", *_):
    md = markdown.Markdown(extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()])
    html = md.convert(markdown_text)
    search_template = get_template('public_pages/elems/basic_area.html')
    return search_template.render(context={"content": html, "layout": layout_overrides})


# The render square function creates a bootstrap card component.
def render_square(markdown_text: str, title: str, layout_overrides: str = "", *_):
    md = markdown.Markdown(extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()])
    html = md.convert(markdown_text)
    search_template = get_template('public_pages/elems/square.html')
    return search_template.render(context={"content": html, "layout": layout_overrides, "title": title})


# The render find function creates a bootstrap card with a search field for finding books.
def render_find(markdown_text: str, title: str, layout_overrides: str = "", *_):
    md = markdown.Markdown(
        extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()], )

    html = md.convert(markdown_text)
    search_template = get_template('public_pages/elems/search_field.html')
    return search_template.render(context={"content": html, "layout": layout_overrides})


def get_open():
    import urllib.request
    try:
        f = urllib.request.urlopen(settings.IS_OPEN_URL, timeout=120)
        is_open_result = str(f.read()).lower()
    except urllib.error.URLError as e:
        logging.error(e)
        return False
    return "true" in is_open_result


# The render trafficlight function creates a trafficlight that shows whether the DK is open
def render_trafficlight(markdown_text: str, title: str, layout_overrides: str = "", *_):
    search_template = get_template('public_pages/elems/traffic_light.html')
    return search_template.render(context={"open": get_open(), "layout": "w-96"})


def start_row(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '<div class="grow flex flex-col lg:flex-row gap-3 {layout}">'.format(layout=layout_overrides)


def end_row(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '</div>'


def start_column(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '<div class="grow flex flex-col gap-3 {layout}">'.format(layout=layout_overrides)


def end_column(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '</div>'


CMDS = {
    "base": render_base_section,
    "square": render_square,
    "search": render_find,
    "yt": render_yt,
    "light": render_trafficlight,
    "interrupt": render_interrupt,
    "start_row": start_row,
    "end_row": end_row,
    "start_column": start_column,
    "end_column": end_column,
}


def get_overrides() -> str:
    return "w-full md:flex-1"


# The render_md function is the main rendering function.
# It collects lines if they are not lines that start new components. If they are a line that starts a new component
# then the previous component is rendered, and a new one is started.
def render_md(markdown_text: str):
    lines = ""
    result = ""
    title = ""
    cms = None
    first_line = True
    for line in markdown_text.split("\n"):
        # Set the title of the current component
        if line.startswith("#!title"):
            title = line[7:].strip()
        elif line.startswith("#!mdflex"):
            pass
        elif line.startswith("#!lgflex"):
            pass

        # new component barrier
        elif line.startswith("#!"):
            if not first_line:
                result += CMDS[cms[0]](lines, title, layout_overrides=get_overrides())
            cms = line[2:].strip().split(" ")
            # Basic sanity check: does the command exist at all
            if cms[0] not in CMDS.keys():
                return cms[0] + " : not a valid keyword"
            lines = ""
            title = ""
        else:
            lines += "\n" + line
        first_line = False
    # If no specific blocks are made, make a 12/12 block with *everything*
    if cms is None:
        cms = ["base"]
    result += CMDS[cms[0]](lines, title, layout_overrides=get_overrides())
    return result


# Check if page rendering should be forbidden, based on user credentials
def forbid_showing_page(page: PublicPage, is_anonymous: bool, member: Member, current_date=None):
    committee_check = False
    if is_anonymous and (page.only_for_logged_in or page.only_for_current_members):
        return True
    if page.only_for_current_members and not member.is_currently_member(current_date):
        return True
    if len(page.limited_to_committees.all()) > 0:
        if is_anonymous:
            committee_check = True
        elif member is None:
            committee_check = True
        else:
            committee_check = True
            for c in page.limited_to_committees.all():
                if c in member.committees.all():
                    committee_check = False
    return committee_check


def view_named_page(request, page_name, sub_page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    can_edit = False

    if not request.user.is_anonymous and (request.user
                                          and (hasattr(request.user, 'member')
                                               and page_group.committees in request.user.member.committees.all())) \
            or request.user.has_perm('public_pages.change_publicpage'):
        can_edit = True

    page = get_object_or_404(PublicPage, name=sub_page_name, group=page_group)
    is_anonymous = request.user and request.user.is_anonymous
    member = hasattr(request.user, "member") and request.user.member
    if forbid_showing_page(page, is_anonymous, member):
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
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

    if forbid_showing_page(page, request.user.is_anonymous, request.user.member):
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    can_edit = False
    if not request.user.is_anonymous and (
            request.user.member and page_group.committees in request.user.member.committees.all()) \
            or request.user.has_perm('public_pages.change_publicpage'):
        can_edit = True
    if not can_edit:
        return HttpResponse("cannot edit")

    if request.method == 'POST':
        form = PageEditForm(request.POST, instance=page)
        rights_form = PageAccessForm(request.POST, instance=page)
        edit_form = EditForm(request.POST, instance=page)
        if form.is_valid() and rights_form.is_valid() and edit_form.is_valid():
            form.save()
            rights_form.save()
            edit_form.save()

            return HttpResponseRedirect(reverse('named_page', args=(page_name, sub_page_name)))
        else:
            print("ERROR")
    else:
        form = PageEditForm(instance=page)
        rights_form = PageAccessForm(instance=page)
        edit_form = EditForm(instance=page)
    return render(request, 'public_pages/page_edit_form.html',
                  {'MY_URL': settings.BASE_URL, 'form': form, 'page': page, 'rights_form': rights_form,
                   "edit_form": edit_form})


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
        instance = PublicPage.objects.create(group_id=page_group.id, name=request.POST['name'])
        form = PageEditForm(request.POST, instance=instance)
        rights_form = PageAccessForm(request.POST, instance=instance)
        edit_form = EditForm(request.POST, instance=instance)
        if form.is_valid() and rights_form.is_valid() and edit_form.is_valid():
            form.save()
            rights_form.save()
            edit_form.save()
            return HttpResponseRedirect(reverse('named_page', args=(instance.group.name, instance.name)))
        else:
            instance.delete()
    else:
        instance = PublicPage(group=page_group)
        form = PageEditForm(instance=instance)
        rights_form = PageAccessForm(instance=instance)
        edit_form = EditForm(instance=instance)
    return render(request, 'public_pages/page_edit_form.html',
                  {'MY_URL': settings.BASE_URL, 'form': form, 'rights_form': rights_form, "edit_form": edit_form})


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


@permission_required('public_pages.change_publicpage')
def list_uploads(request):
    uploads = FileUpload.objects.all()
    return render(request, 'public_pages/uploads_list.html', {'uploads': uploads})


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

    return render(request, 'public_pages/upload_form.html', {"form": form, "special": special})


@permission_required('public_pages.change_publicpage')
def delete_upload(request, pk):
    page = FileUpload.objects.filter(pk=pk)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete attachment with name " + page.first().name})
    page.delete()

    return redirect('list_uploads')

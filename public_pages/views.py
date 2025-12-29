from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from members.models import Member
from public_pages.forms import PageEditForm, UploadFileForm, PageAccessForm, EditForm
from public_pages.models import PublicPageGroup, PublicPage, FileUpload
from public_pages.renderer.renderer import render_md


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


def view_index_page(request, page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_name)
    is_anonymous = not not (request.user and request.user.is_anonymous)

    if not page_group.publicly_indexed and is_anonymous:
        return HttpResponseForbidden("You do not have permission to view this resource.")
    pages = PublicPage.objects.filter(group=page_group).order_by("title")
    index_path = '_index'
    data = {'group': page_group, 'index_path': index_path}
    page_data = []
    data['index_title'] = "Index for %s" % page_group.name
    member = hasattr(request.user, "member") and request.user.member
    for page in pages:
        dat = {
            'can_view': not forbid_showing_page(page, is_anonymous, member),
            'page': page,
        }
        if page.name == '_index':
            data['index_html'] = render_md(page.text)
            data['index_title'] = page.title
        else:
            page_data.append(dat)

    data['pages'] = page_data

    if not request.user.is_anonymous and (request.user
                                          and (hasattr(request.user, 'member')
                                               and page_group.committees in request.user.member.committees.all())) \
            or request.user.has_perm('public_pages.change_publicpage'):
        data['can_edit'] = True
    return HttpResponse(render(request, template_name='public_pages/index_page.html',
                               context=data))


def view_named_page(request, page_group_name, page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_group_name)
    can_edit = False
    if page_name == '_index':
        return HttpResponseRedirect(reverse('index_page', args=(page_group_name,)))
    if not request.user.is_anonymous and (request.user
                                          and (hasattr(request.user, 'member')
                                               and page_group.committees in request.user.member.committees.all())) \
            or request.user.has_perm('public_pages.change_publicpage'):
        can_edit = True

    page = get_object_or_404(PublicPage, name=page_name, group=page_group)
    is_anonymous = request.user and request.user.is_anonymous
    member = hasattr(request.user, "member") and request.user.member
    if forbid_showing_page(page, is_anonymous, member):
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    html = render_md(page.text, show_errors=can_edit)

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
    return HttpResponse(render_md(request.POST["text"], show_errors=True))


@login_required
def test_render_function(request):
    return HttpResponse(render(request, template_name='public_pages/page_edit.html', context={}))


@login_required
@transaction.atomic
def edit_named_page(request, page_group_name, page_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_group_name)
    page = get_object_or_404(PublicPage, name=page_name, group=page_group)

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
            if form.instance.name == '_index':
                return HttpResponseRedirect(reverse('index_page', args=(page_group_name,)))
            return HttpResponseRedirect(reverse('named_page', args=(page_group_name, page_name)))
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
def new_named_page(request, page_group_name):
    page_group = get_object_or_404(PublicPageGroup, name=page_group_name)
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
        form = PageEditForm(instance=instance, initial={'name': request.GET.get('page_name', '')})
        rights_form = PageAccessForm(instance=instance)
        edit_form = EditForm(instance=instance)
    return render(request, 'public_pages/page_edit_form.html',
                  {'name': request.GET.get('page_name', ''), 'MY_URL': settings.BASE_URL, 'form': form,
                   'rights_form': rights_form, "edit_form": edit_form})


@permission_required('public_pages.view_publicpage')
def list_named_pages(request):
    pages = PublicPage.objects.order_by('name').distinct()
    return render(request, 'public_pages/page_list.html',
                  {'MY_URL': settings.BASE_URL, 'pages': pages, 'groups': PublicPageGroup.objects.all()})


@permission_required('public_pages.delete_publicpage')
@transaction.atomic
def delete_page(request, pk, hx_enabled=False):
    page = PublicPage.objects.filter(pk=pk)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete page with name " + page.first().name})

    page.delete()

    return redirect('list_pages')


@permission_required('public_pages.change_publicpage')
def list_uploads(request):
    uploads = FileUpload.objects.all()

    uploads = list(uploads)
    uploads.sort(key=lambda f: f.file.name.upper())
    return render(request, 'public_pages/uploads_list.html', {'uploads': uploads})


@permission_required('public_pages.change_publicpage')
def new_upload(request):
    special = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()

            return redirect('list_uploads')

    else:
        form = UploadFileForm()

    return render(request, 'public_pages/upload_form.html', {"form": form, "special": special})


@permission_required('public_pages.change_publicpage')
def delete_upload(request, pk):
    pages = FileUpload.objects.filter(pk=pk)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete file " + pages.first().file.name})
    for page in pages:
        page.file.delete()
        page.delete()

    return redirect('list_uploads')

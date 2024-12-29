from random import random

from django import template
from django.urls import reverse
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from config.menu import MenuItem

register = template.Library()


@register.simple_tag
def menu_data(location, perms, is_anonymous):
    menu = get_menu_item_list()
    result = []
    for item in menu:
        if item.location != location:
            continue
        if not item.anonymous and is_anonymous:
            continue
        if (not item.permission) or item.permission in perms:
            result.append(item)
            if item.sub_items is None:
                continue
            for subItem in item.sub_items:
                if subItem.permission and subItem.permission not in perms:
                    item.sub_items.remove(subItem)
    return result


# This function creates a large list of MenuItems, which are in essense a combined menu for the top- and sidebars.
# Should probably be refactored into a much simpler code structure.
def get_menu_item_list():
    my_menu = []
    my_menu.append(MenuItem('Book Search', reverse('works.list'), None, 'top', [], icon='fa fa-book', anonymous=True))
    my_menu.append(MenuItem("Our Activities", reverse('named_page', args=('basic', 'member',)), None, 'top', [],
                            icon='fa fa-user', anonymous=True))
    my_menu.append(
        MenuItem('Become a member', reverse('named_page', args=('basic', 'member',)), None, 'top', [], anonymous=True,
                 icon='fa fa-user'))
    my_menu.append(MenuItem("Become Active", reverse('named_page', args=('basic', 'member',)), None, 'top', [],
                            icon='fa fa-user', anonymous=True))


    my_menu.append(
        MenuItem('Board / Committees', reverse('named_page', args=('basic', 'committees',)), None, 'top-left', [],
                 icon='fa fa-users'))
    my_menu.append(
        MenuItem('Konnichiwa', reverse('named_page', args=('konnichiwa', 'home',)), None, 'top-left', [], icon=''))

    # my_menu.append(MenuItem('Corona', reverse('named_page', args=('basic', 'corona',)), None, 'top-right', [], icon='fa fa-exclamation-circle'))
    my_menu.append(
        MenuItem('About', reverse('named_page', args=('basic', 'about',)), None, 'top-right', [], icon='fa fa-user'))
    my_menu.append(MenuItem('Contact', reverse('named_page', args=('basic', 'contact',)), None, 'top-right', [],
                            icon='fa fa-info'))

    my_menu.append(MenuItem('Login', reverse('login'), None, 'top-right', [], anonymous=True, icon='fa fa-sign-in-alt'))
    my_menu.append(
        MenuItem('Logout', reverse('logout'), None, 'top-right', [], anonymous=False, icon='fa fa-sign-out-alt',
                 is_logout=True))

    my_menu.append(MenuItem('Members', reverse('members.list'), 'members.view_member', 'sidebar', [], anonymous=None,
                            icon='fa fa-user'))
    my_menu.append(
        MenuItem('Lendings', reverse('lendings.list'), 'lendings.view_lending', 'sidebar', [], anonymous=None,
                 icon='fa fa-bookmark'))
    my_menu.append(
        MenuItem('Reservations', reverse('lendings.reserve.list'), 'reservations.view_reservation', 'sidebar', [],
                 anonymous=None, icon='fa fa-bookmark'))
    holiday_item = MenuItem('Holidays', reverse('holiday.list'), 'config.view_holiday', 'sidebar', [], anonymous=None,
                            icon='fa fa-plane')
    my_menu.append(
        MenuItem('Settings', reverse('logout'), None, 'sidebar', [holiday_item], only_subitems=True, icon='fa fa-cogs'))

    uploads = MenuItem('Uploads', reverse('list_uploads'), 'public_pages.change_publicpage', 'sidebar', [],
                       anonymous=None, icon='fa fa-upload')
    web_management = MenuItem('List Web Pages', reverse('list_pages'), 'public_pages.view_publicpage', 'sidebar', [],
                              anonymous=None, icon='fa fa-newspaper')
    my_menu.append(
        MenuItem('Web Management', reverse('logout'), None, 'sidebar', [web_management, uploads], only_subitems=True,
                 icon='fa fa-globe'))

    new_work = MenuItem('New Work', reverse('works.publication.new'), 'works.add_publication', 'sidebar', [],
                        anonymous=None, icon='fa fa-book')
    new_series = MenuItem('New Series', reverse('series.new'), 'series.add_series', 'sidebar', [], anonymous=None,
                          icon='fa fa-book')
    new_creator = MenuItem('New Author', reverse('creator.new'), 'creators.add_creator', 'sidebar', [], anonymous=None,
                           icon='fa fa-book')
    inventarisation = MenuItem('Inventarisations', reverse('inventarisation.list'),
                               'inventarisation.view_inventarisation', 'sidebar', [], anonymous=None,
                               icon='fa fa-clipboard-list')
    recode_list = MenuItem('Recode list', reverse('recode.list'), 'recode.view_recode', 'sidebar', [], anonymous=None,
                           icon='fa fa-clipboard-list')
    codes = MenuItem('Book Codes', reverse('book_code.code_list'), 'works.change_work', 'sidebar', [], anonymous=None,
                     icon='fa fa-clipboard-list')

    my_menu.append(
        MenuItem('Catalog Management', reverse('logout'), None, 'sidebar',
                 [new_work, new_series, new_creator, inventarisation, recode_list, codes], only_subitems=True,
                 icon='fa fa-book'))
    anon_members = MenuItem('Anonymous users', reverse('members.list.anon'), 'members.change_member', 'sidebar', [],
                            anonymous=None, icon='fa fa-clipboard-list')
    member_stats = MenuItem('Member Statistics', reverse('datamining.membership_stats'), 'members.change_member',
                            'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')
    lending_stats = MenuItem('Lending Statistics', reverse('datamining.lending_stats'), 'works.view_work', 'sidebar',
                             [], anonymous=None, icon='fa fa-clipboard-list')

    members_list = MenuItem('Member Filter', reverse('datamining.members'), 'members.change_member', 'sidebar', [],
                            anonymous=None, icon='fa fa-clipboard-list')
    my_menu.append(MenuItem('Datamining', reverse('logout'), None, 'sidebar',
                            [members_list, anon_members, member_stats, lending_stats], only_subitems=True,
                            icon='fa fa-book'))
    my_menu.append(MenuItem('Docs', reverse('named_page', args=("docs", "home",)), None, 'sidebar', [], anonymous=False,
                            icon='fa fa-book'))

    return my_menu

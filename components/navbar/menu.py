# In this file we define how the menu works.
# We first define some classes to structure the menu
# Then there's a list of some menu-items
# Finally we define the menus we have.
from copy import deepcopy

from django.urls import reverse

from bellettrie_library_system import settings


class SuperMenu:
    def __init__(self, label, *items):
        self.label = label
        self.items = items

    def is_super(self):
        return True

    def is_visible(self, perms):
        for item in self.items:
            if item.is_visible(perms):
                return True
        return False


class Separator:
    def is_separator(self):
        return True

    def is_visible(self, perms):
        return True


class Item:
    def __init__(self, label, url, required_perm=None):
        self.label = label
        self.url = url
        self.perm = required_perm

    def is_super(self):
        return False

    def is_visible(self, perms):
        return self.perm is None or self.perm in perms


ITEM_SEARCH = Item("Book Search", reverse('homepage'))
ACTIVITIES = Item("Our Activities", reverse('named_page', args=(settings.STANDARD_PAGE_GROUP, 'member',)))
BECOME_MEMBER = Item("Become Member", reverse('named_page', args=('basic', 'member',)))

MEMBERS = Item("Members", reverse("members.list", ), required_perm="members.view_member")
LENDINGS = Item("Lendings", reverse('lendings.list'), required_perm="lendings.view_lending")
RESERVATIONS = Item("Reservations", reverse('reservations.list'), required_perm="reservations.view_reservation", )

HOLIDAYS = Item("Holidays", reverse("holiday.list"), required_perm="holidays.view_holiday")
SETTINGS = SuperMenu("Settings", HOLIDAYS)

UPLOADS = Item("Uploads", reverse("list_uploads"), required_perm="public_pages.change_publicpage")
WEB_PAGES = Item("Pages", reverse("list_pages"), required_perm="public_pages.view_publicpage")
WEB_MANAGEMENT = SuperMenu("Web Management", UPLOADS, WEB_PAGES)

NEW_WORK = Item("New Work", reverse('works.publication.new'), required_perm="works.add_publication")
NEW_SERIES = Item("New Series", reverse("series.new"), required_perm="series.add_series")
NEW_CREATOR = Item("New Author", reverse("creator.new"), required_perm="creator.add_creator")
INVENTARISATION = Item("Inventarisations", reverse("inventarisation.list"),
                       required_perm="inventarisation.view_inventarisation")
RECODE_LIST = Item("Recode List", reverse("recode.list"), required_perm="recode.view_recode")
CODES = Item("Book Codes", reverse("book_code.code_list"), required_perm="works.change_work")
CATALOG_MANAGEMENT = SuperMenu("Catalog Management", NEW_WORK, NEW_SERIES, NEW_CREATOR, INVENTARISATION, RECODE_LIST,
                               CODES)

ANON_MEMBERS = Item("Anonymous Users", reverse("members.list.anon"), required_perm="members.change_member")
MEMBER_STATS = Item("Member Statistics", reverse("datamining.membership_stats"), required_perm="members.view_member")
LENDING_STATS = Item("Lending Statistics", reverse("datamining.lending_stats"), required_perm="works.view_work")
MEMBER_LIST = Item("Member Filter", reverse("datamining.members"), required_perm="members.view_member")
DATAMINING = SuperMenu("Datamining", ANON_MEMBERS, MEMBER_STATS, LENDING_STATS, MEMBER_LIST)

DOCS = Item("Docs", reverse('named_page', args=("docs", "home",)), required_perm="docs.view_docs")

top_bar = [
    ITEM_SEARCH,
    ACTIVITIES,
    BECOME_MEMBER,
]

sidebar = [
    MEMBERS,
    LENDINGS,
    RESERVATIONS,
    SETTINGS,
    WEB_MANAGEMENT,
    CATALOG_MANAGEMENT,
    DATAMINING,
    DOCS
]

footer = [
    SuperMenu("Socials", Item("Hyves", None), Item("Insta", None), Item("Facebook", None)),
    SuperMenu("Legal", Item("Nonsense", None))
]


def menu_with_only_right_permissions(items, perms):
    result = []
    for item in items:
        if item.is_super():
            it = deepcopy(item)
            it.items = []
            for itm in item.items:
                if itm.is_visible(perms):
                    it.items.append(itm)
            if len(it.items) > 0:
                result.append(it)
        else:
            result.append(item)
    return result

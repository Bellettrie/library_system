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
    def __init__(self, label, url, perm=None):
        self.label = label
        self.url = url
        self.perm = perm

    def is_super(self):
        return False

    def is_visible(self, perms):
        return self.perm is None or self.perm in perms


DOCS = Item("Docs", reverse('index_page', args=("docs",)), perm="works.view_work")

top_bar = [
    Item("Book Search", reverse('works.list')),
    SuperMenu(
        "Activities",
        # Item("Activities", reverse('named_page', args=(settings.STANDARD_PAGE_GROUP, 'activities',))),
        Item("Writing", reverse('named_page', args=("writing", "home",))),
        Item("Konnichiwa", reverse('named_page', args=("konnichiwa", "home",))),

    ),
    Item("Become Member", reverse('named_page', args=(settings.STANDARD_PAGE_GROUP, 'member',))),
]

MEMBERS = Item("Members", reverse("members.list", ), perm="members.change_member")
LENDINGS = Item("Lendings", reverse('lendings.list'), perm="lendings.change_lending")
RESERVATIONS = Item("Reservations", reverse('reservations.list'), perm="reservations.view_reservation", )

HOLIDAYS = Item("Holidays", reverse("config.holiday.list"), perm="config.view_holiday")
SETTINGS = SuperMenu("Settings", HOLIDAYS)

UPLOADS = Item("Uploads", reverse("list_uploads"), perm="public_pages.change_publicpage")
WEB_PAGES = Item("Pages", reverse("list_pages"), perm="public_pages.view_publicpage")
WEB_MANAGEMENT = SuperMenu("Web Management", UPLOADS, WEB_PAGES)

NEW_WORK = Item("New Work", reverse('works.publication.new'), perm="works.add_publication")
NEW_SERIES = Item("New Series", reverse("series.new"), perm="series.add_series")
NEW_CREATOR = Item("New Author", reverse("creator.new"), perm="creators.change_creator")
INVENTARISATION = Item("Inventarisations", reverse("inventarisations.inventarisation.list"),
                       perm="inventarisation.view_inventarisation")
RECODE_LIST = Item("Recode List", reverse("recode.list"), perm="recode.view_recode")
CODES = Item("Book Codes", reverse("book_code.code_list"), perm="works.change_work")
CATALOG_MANAGEMENT = SuperMenu("Catalog Management", NEW_WORK, NEW_SERIES, NEW_CREATOR, INVENTARISATION, RECODE_LIST,
                               CODES)

ANON_MEMBERS = Item("Anonymous Users", reverse("members.list.anon"), perm="members.view_member")
MEMBER_STATS = Item("Member Statistics", reverse("datamining.membership_stats"), perm="members.view_member")
LENDING_STATS = Item("Lending Statistics", reverse("datamining.lending_stats"), perm="works.view_work")
MEMBER_LIST = Item("Member Filter", reverse("datamining.members"), perm="members.view_member")
DATAMINING = SuperMenu("Reporting", ANON_MEMBERS, MEMBER_STATS, LENDING_STATS, MEMBER_LIST)


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
    SuperMenu(
        "Our Association",
        Item("Contact Us", reverse('named_page', args=(settings.STANDARD_PAGE_GROUP, "contact",))),
        Item("Official Documents", reverse('named_page', args=(settings.STANDARD_PAGE_GROUP, "about",))),
        Item("Privacy Policy", reverse('named_page', args=(settings.STANDARD_PAGE_GROUP, "privacy",)))),
    SuperMenu(
        "Internal Documentation",
        Item("Documentation", reverse('index_page', args=("docs",)), perm="works.view_work"),
        Item("Website Source Code", "https://github.com/bellettrie/library_system", perm="works.view_work"),
    ),

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
            if item.is_visible(perms):
                result.append(item)
    return result

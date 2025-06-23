from pydoc import visiblename

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
    def __init__(self, label, url, visible_perm=None):
        self.label = label
        self.url = url
        self.perm = visible_perm

    def is_super(self):
        return False

    def is_visible(self, perms):
        return self.perm is None or self.perm in perms


ITEM_SEARCH = Item("Book Search", reverse('homepage'))
ACTIVITIES = Item("Our Activities", reverse('named_page', args=(settings.STANDARD_PAGE_GROUP, 'member',)))
BECOME_MEMBER = Item("Become Member", reverse('named_page', args=('basic', 'member',)))

MEMBERS = Item("Members", reverse("members.list", ), visible_perm="members.view_member")
LENDINGS = Item("Lendings", reverse('lendings.list'), visible_perm="lendings.view_lending")
RESERVATIONS = Item("Reservations", reverse('reservations.list'), visible_perm="reservations.view_reservation", )

HOLIDAYS = Item("Holidays", reverse("holiday.list"), visible_perm="holidays.view_holiday")
SETTINGS = SuperMenu("Settings", HOLIDAYS)

UPLOADS = Item("Uploads", reverse("list_uploads"), visible_perm="public_pages.change_publicpage")
WEB_PAGES = Item("Pages", reverse("list_pages"), visible_perm="public_pages.view_publicpage")
WEB_MANAGEMENT = SuperMenu("Web Management", UPLOADS, WEB_PAGES)

NEW_WORK = Item("New Work", reverse('works.publication.new'), visible_perm="works.add_publication")
NEW_SERIES = Item("New Series", reverse("series.new"), visible_perm="series.add_series")
NEW_CREATOR = Item("New Author", reverse("creator.new"), visible_perm="creator.add_creator")
INVENTARISATION = Item("Inventarisations", reverse("inventarisation.list"),
                       visible_perm="inventarisation.view_inventarisation")
RECODE_LIST = Item("Recode List", reverse("recode.list"), visible_perm="recode.view_recode")
CODES = Item("Book Codes", reverse("book_code.code_list"), visible_perm="works.change_work")
CATALOG_MANAGEMENT = SuperMenu("Catalog Management", NEW_WORK, NEW_SERIES, NEW_CREATOR, INVENTARISATION, RECODE_LIST,
                               CODES)

ANON_MEMBERS = Item("Anonymous Users", reverse("members.list.anon"), visible_perm="members.change_member")
MEMBER_STATS = Item("Member Statistics", reverse("datamining.membership_stats"), visible_perm="members.view_member")
LENDING_STATS = Item("Lending Statistics", reverse("datamining.lending_stats"), visible_perm="works.view_work")
MEMBER_LIST = Item("Member Filter", reverse("datamining.members"), visible_perm="members.view_member")
DATAMINING = SuperMenu("Datamining", ANON_MEMBERS, MEMBER_STATS, LENDING_STATS, MEMBER_LIST)

DOCS = Item("Docs", reverse('named_page', args=("docs", "home",)), visible_perm="docs.view_docs")

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


def right_limited_menu(items, perms):
    result = []
    for item in items:
        if item.is_visible(perms):
            result.append(item)
    return result

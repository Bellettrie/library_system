from django.shortcuts import render
from django.urls import reverse


class MenuItem:
    def __init__(self, title, url, permission, location, sub_items, anonymous=None, only_subitems=False):
        self.title = title
        self.url = url
        self.permission = permission
        self.sub_items = sub_items
        self.location = location
        self.anonymous = anonymous
        self.only_subitems = only_subitems

    def permits(self, request):
        return (self.permission is None or request.user.has_perm(self.permission)) and (self.anonymous is None or request.user.is_anonymous == self.anonymous) and (
            not self.only_subitems or len(self.rendered_sub_items(request)) > 0)

    def rendered_sub_items(self, request):
        lst = []
        for item in self.sub_items:
            if item.permits(request):
                lst.append(item)
        return lst

    def render(self, request):
        sub_items = self.rendered_sub_items(request)
        return render(request, 'render_menu_item.html', context={'menu': self, 'has_sub_items': len(sub_items) > 0, 'sub_items': sub_items})

    def get_title_shortened(self):
        return self.title.replace(" ", "")


my_menu = [MenuItem('test', reverse('login'), None, 'top', [], anonymous=True)]
my_menu.append(MenuItem('Home', reverse('homepage'), None, 'top-left', []))
my_menu.append(MenuItem('Catalog', reverse('works.list'), None, 'top-left', []))
my_menu.append(MenuItem('Become a member', reverse('named_page', args=('basic', 'member',)), None, 'top-left', []))
my_menu.append(MenuItem('Board / Committees', reverse('named_page', args=('basic', 'committees',)), None, 'top-left', []))
my_menu.append(MenuItem('Konnichiwa', reverse('named_page', args=('konnichiwa', 'home',)), None, 'top-left', []))

my_menu.append(MenuItem('Corona', reverse('named_page', args=('basic', 'corona',)), None, 'top-right', []))
my_menu.append(MenuItem('About', reverse('named_page', args=('basic', 'about',)), None, 'top-right', []))
my_menu.append(MenuItem('Contact', reverse('named_page', args=('basic', 'contact',)), None, 'top-right', []))

my_menu.append(MenuItem('Login', reverse('login'), None, 'top-right', [], anonymous=True))
my_menu.append(MenuItem('Logout', reverse('logout'), None, 'top-right', [], anonymous=False))

my_menu.append(MenuItem('Catalog', reverse('works.list'), None, 'sidebar', [], anonymous=False))
my_menu.append(MenuItem('Members', reverse('members.list'), 'members.view_member', 'sidebar', [], anonymous=None))
my_menu.append(MenuItem('Lendings', reverse('lendings.list'), 'lendings.view_lending', 'sidebar', [], anonymous=None))
holiday_item = MenuItem('Holidays', reverse('holiday.list'), 'config.view_holiday', 'sidebar', [], anonymous=None)
my_menu.append(MenuItem('Settings', reverse('logout'), None, 'sidebar', [holiday_item], only_subitems=True))

uploads = MenuItem('Uploads', reverse('list_uploads'), 'public_pages.change_publicpage', 'sidebar', [], anonymous=None)
web_management = MenuItem('List Web Pages', reverse('list_pages'), 'public_pages.view_publicpage', 'sidebar', [], anonymous=None)
my_menu.append(MenuItem('Web Management', reverse('logout'), None, 'sidebar', [web_management, uploads], only_subitems=True))

new_work = MenuItem('New Work', reverse('works.publication.new'), 'works.add_publication', 'sidebar', [], anonymous=None)
inventarisation = MenuItem('Inventarisations', reverse('inventarisation.list'), 'inventarisation.view_inventarisation', 'sidebar', [], anonymous=None)
my_menu.append(MenuItem('Catalog Management', reverse('logout'), None, 'sidebar', [new_work, inventarisation], only_subitems=True))

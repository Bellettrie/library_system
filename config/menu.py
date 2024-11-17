from django.shortcuts import render
from django.urls import reverse


class MenuItem:
    def __init__(self, title, url, permission, location, sub_items, anonymous=None, only_subitems=False, icon=None,
                 is_logout=False):
        self.title = title
        self.url = url
        self.permission = permission
        self.sub_items = sub_items
        self.location = location
        self.anonymous = anonymous
        self.only_subitems = only_subitems
        self.icon = icon
        self.is_logout = is_logout

    def permits(self, request):
        return ((self.permission is None or request.user.has_perm(self.permission))
                and (self.anonymous is None or request.user.is_anonymous == self.anonymous)
                and (not self.only_subitems or len(self.rendered_sub_items(request)) > 0)
                )

    def rendered_sub_items(self, request):
        lst = []

        for item in self.sub_items:
            if item.permits(request):
                lst.append(item)
        return lst

    def render(self, request):
        sub_items = self.rendered_sub_items(request)
        return render(request, 'config/render_menu_item.html',
                      context={'menu': self, 'has_sub_items': len(sub_items) > 0, 'sub_items': sub_items})

    def get_title_shortened(self):
        return self.title.replace(" ", "")
    def __str__(self):
        return "{title} ? ".format(title=self.title)
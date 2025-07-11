from typing import Optional

from django.template.context import Context

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from components.navbar.menu import menu_with_only_right_permissions, top_bar


@register("navbar.Item")
class Item(Component):

    def get_context_data(self, text, my_url, *args, location="aaa", extra_classes="", **kwargs):
        # skip absolute urls
        if not (my_url == "" or my_url.startswith("/") or my_url.startswith("https://")):
            my_url = reverse(my_url, args=args)
        return {
            "my_url": my_url,
            "text": text,
            "location": location,
            "extra_classes": extra_classes,
        }

    def get_template_name(self, context: Context) -> Optional[str]:
        location = context.get("location")
        if location == "top":
            return "navbar/items/top_menu.html"
        if location == "mob":
            return "navbar/items/mobile.html"
        return "navbar/items/sidebar.html"


@register("navbar.Navbar")
class Navbar(Component):
    template_name = "navbar/navbar.html"

    def get_context_data(self, perms):
        return {
            "menu_buttons": menu_with_only_right_permissions(top_bar, perms),
            "logo_debug": settings.UPSIDE_DOWN,
            "logo_name": settings.LIBRARY_NAME,
            "logo_image": settings.LIBRARY_IMAGE_URL,
        }


@register("navbar.Logo")
class Logo(Component):
    def get_context_data(self, debug, name, logo):
        return {
            "debug": debug,
            "name": name,
            "logo": logo,
        }

    template_name = "navbar/logo.html"

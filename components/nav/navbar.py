# In a file called [project root]/components/calendar/calendar.py
from typing import Optional

from django.template.context import Context

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


def get_top_menu():
    pass


@register("top-item")
class NavItem(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, text, my_url, *args, location="aaa", perm=None, **kwargs):
        # skip absolute urls
        if not (my_url =="" or my_url.startswith("/") or my_url.startswith("https://")):
            my_url = reverse(my_url, args=args)
        return {
            "my_url": my_url,
            "text": text,
            "location": location,
            "perm": perm
        }

    def get_template_name(self, context: Context) -> Optional[str]:
        l = context.get("location")
        if l == "top":
            return "nav/items/top_menu.html"
        if l == "mob":
            return "nav/items/mobile.html"
        return "nav/items/sidebar.html"


@register("top_nav")
class TopNav(Component):
    template_name = "nav/navbar.html"

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self):
        left_items = []
        mobile_items = []
        for it in GET_MENU():
            if it.location == "top":
                left_items.append(it)
                mobile_items.append(it)

        return {
            "menu_buttons": left_items,
            "mobile_items": mobile_items,
            "logo_debug": settings.UPSIDE_DOWN,
            "logo_name": settings.LIBRARY_NAME,
            "logo_image": settings.LIBRARY_IMAGE_URL,
        }

    class Media:
        css = "nav/navbar.css"


@register("logo")
class Logo(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, debug, name, logo):
        return {
            "debug": debug,
            "name": name,
            "logo": logo,
        }

    template_name = "nav/logo.html"
    css: types.css = """
.rotate4{ /*upside down*/
    -webkit-transform:rotate(180deg);
    -moz-transform:rotate(180deg);
    -o-transform:rotate(180deg);
    -ms-transform:rotate(180deg);
    transform:rotate(180deg);
}

"""


@register("top-item-logout")
class TopLogoutItem(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, text, *args):
        return {
            "link_url`": "logout",
            "text": text,
        }

    template: types.django_html = """
     <a class="vertical align-top"> </a>
    <form method="post" action="{% url 'logout' %}" class="form-inline renderLogoutformstyle align-top">
        {% csrf_token %}
        <input class="btn btn-outline renderLogoutfakeURL" type="submit" value="{{ text }}">
    </form>
    """
    css: types.css = """
       .renderLogoutfakeURL {
        font-family: 'Rubik', sans-serif;
        font-size: 1vw;
        color: grey;
        padding: 0;
        border: 0;
        margin-top: -.8vw;
    }

    .renderLogoutformstyle {
        display: inline;
        padding-left: .1vw;
        font-family: 'Rubik', sans-serif;
        font-size: 1vw;
        color: grey;
    }
    """

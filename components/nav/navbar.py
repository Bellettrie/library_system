# In a file called [project root]/components/calendar/calendar.py
from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("top_nav")
class TopNav(Component):
    template_name = "nav/navbar.html"

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self):
        left_items = []
        right_items = []
        for it in GET_MENU():
            print(it.location)
            if it.location == "top-left":
                left_items.append(it)
            if it.location == "top-right":
                right_items.append(it)
        return {
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

    template: types.django_html = """
    {% load static %}
    <a href="{% url 'homepage' %}" class="logo-part" style=" text-align: center;width:100%; "><img {% if debug %}class="rotate4"{% endif %}
                src="{% static logo %}"

                style="height:75px;     font-family: 'Pangolin'; "/> {{ name }}
        </a>
    """
    css: types.css = """    
.rotate4{ /*upside down*/
    -webkit-transform:rotate(180deg);
    -moz-transform:rotate(180deg);
    -o-transform:rotate(180deg);
    -ms-transform:rotate(180deg);
    transform:rotate(180deg);
}
"""


@register("top-item")
class TopMenuItem(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, text, my_url, *args):
        # skip absolute urls
        print(my_url)
        if not (my_url.startswith("/") or my_url.startswith("https://")):
            my_url = reverse(my_url, *args)
        print("U", my_url)
        return {
            "my_url": my_url,
            "text": text,
        }

    template: types.django_html = """
            <a href="{{ my_url }}" class="vertical hiddenMobile align-top">{{ text }}</a>    
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

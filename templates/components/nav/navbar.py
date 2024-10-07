from django.conf import settings
from django_components import component

from bellettrie_library_system.base_settings import GET_MENU


@component.register("navbar")
class Navbar(component.Component):
    template_name = "components/nav/navbar.html"

    def get_context_data(self):
        return {"menu": GET_MENU()}

    # class Media:
    #     css = "todo/todo.css"

@component.register("nav-logo")
class Logo(component.Component):
    template_name = "components/nav/logo.html"

    def get_context_data(self):
        return {"name": settings.LIBRARY_NAME}

    # class Media:
    #     css = "todo/todo.css"
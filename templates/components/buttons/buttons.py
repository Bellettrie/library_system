
from django.conf import settings
from django_components import component

from bellettrie_library_system.base_settings import GET_MENU

@component.register("loginButton")
class Login(component.Component):
    template_name = "components/buttons/login.html"

    def get_context_data(self):
        return {"menu": GET_MENU()}

    # class Media:
    #     css = "todo/todo.css"
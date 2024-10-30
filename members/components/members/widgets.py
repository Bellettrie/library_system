# In a file called [project root]/components/calendar/calendar.py
from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("members.search_input")
class SearchInput(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, query=""):
        return {
            "query": query,
        }

    template: types.django_html = """
    <div class="card bg-base-100  shadow-xl rounded-none xl:sticky xl:top-0">
            <div class="card-body">
<form action="/members" method="get" class="items-center gap-2 space-y-4 form-control" >
           <label class="form-control">
             <div class="label">
    <span class="label-text">Member Name</span>
              </div>
                <input id="q" type="text" name="q" value="{{ query }}" class="input input-bordered w-full max-w-xs">
        </label>
    <label class="form-control center">
        <div class="label">
            <span class="label-text">Also Former Members?</span>
        </div>
        <input type="checkbox" id="previous" name="previous"{% if  request.GET.previous %}  checked="checked" {% endif %} class="checkbox checkbox-md" />
    </label>
 <input type="submit" value="Search" class="btn btn-accent gap-2 w-full ">
</form>
</div>
</div>
"""

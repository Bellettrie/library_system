from django import template

register = template.Library()


@register.inclusion_tag('publication_table/buttons/lend_button.html')
def lend_button(item, perms):
    return {"item": item, "perms": perms}


@register.inclusion_tag('publication_table/buttons/finalize_lending_button.html')
def finalize_button(item, perms, member):
    return {"item": item, "perms": perms, "member": member}
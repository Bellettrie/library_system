from django import template

from reservations.models import Reservation

register = template.Library()


@register.inclusion_tag('publication_table/buttons/lend_button.html')
def lend_button(item, perms):
    return {"item": item, "perms": perms}


@register.inclusion_tag('publication_table/buttons/finalize_lending_button.html')
def finalize_button(item, perms, member):
    return {"item": item, "perms": perms, "member": member}


@register.inclusion_tag('publication_table/buttons/finalize_reservation_button.html')
def finish_reservation_button(item, perms, member):
    return {"item": item, "perms": perms, "member": member}


@register.inclusion_tag('publication_table/buttons/extend_button.html')
def extend_button(item, perms, member):
    return {"item": item, "perms": perms, "member": member}


@register.inclusion_tag('publication_table/buttons/return_button.html')
def return_button(item, perms, member):
    return {"item": item, "perms": perms, "member": member}


@register.inclusion_tag('publication_table/buttons/reserve_button.html')
def reserve_button(item, perms, user):
    if hasattr(user, "member"):
        user = user.member
    if user.id is None:
        user = None

    return {"item": item, "perms": perms, "user": user, "member": user}


@register.inclusion_tag('publication_table/buttons/finalize_reservation_button.html')
def finalize_reservation_button(item, perms, member):
    reservation = Reservation.objects.get(item=item, member=member)
    return {"item": item, "perms": perms, "member": member, 'reservation': reservation}


@register.inclusion_tag('publication_table/buttons/cancel_button.html')
def res_cancel_button(item, perms, member):
    reservation = Reservation.objects.get(item=item, member=member)
    return {"item": item, "perms": perms, "member": member, 'reservation': reservation}

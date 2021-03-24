from django import template

from bellettrie_library_system.cross_login import my_encrypt, my_encrypt_from_member
from members.models import Member

register = template.Library()


@register.inclusion_tag('cross_login_url.html')
def get_crosslogin_url(member: Member):
    return {'token': my_encrypt_from_member(member)}

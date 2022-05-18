import datetime

import jwt
from django.conf import settings

from members.models import Committee


class MemberData:
    def __init__(self, name, id, perm_level):
        self.name = name
        self.id = id
        self.perm_level = perm_level


def my_encrypt_from_member(member) -> str:
    lenders = Committee.objects.get(code="LENDERS")
    admins = Committee.objects.get(code="ADMIN")
    board = Committee.objects.get(code="BOARD")
    perm_level = 0
    if lenders in member.committees.all():
        perm_level = 1
    if admins in member.committees.all() or board in member.committees.all():
        perm_level = 2
    return my_encrypt(MemberData(member.name, member.pk, perm_level))


def my_encrypt(member: MemberData) -> str:
    data = {"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2), 'name': member.name, 'id': member.id, 'perms': member.perm_level}
    return jwt.encode(data, settings.CROSS_LOGIN_KEY, algorithm="HS256")


def my_decrypt(data: str) -> MemberData:
    data = jwt.decode(data, settings.CROSS_LOGIN_KEY, algorithms=["HS256"])
    return MemberData(data.get('name'), data.get('id'), data.get('perms'))

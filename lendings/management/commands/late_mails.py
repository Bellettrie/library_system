from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from lendings.models import Lending
from mail.models import mail_member
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from works.models import Item


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        lendings = Lending.objects.filter(handed_in=False)
        late_dict = dict()
        for lending in lendings:
            if lending.is_late():
                my_list = late_dict.get(lending.member, [])
                my_list.append(lending)
                late_dict[lending.member] = my_list
        print("HERE")
        for member in late_dict.keys():
            print(member.name)
            mail_member('mails/late_mail.tpl', {'member': member, 'lendings' : late_dict[member]}, member, True)

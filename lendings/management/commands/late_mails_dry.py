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
        mails = Lending.late_mails(fake=True)
        print(mails)

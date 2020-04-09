from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        committees = [(KASCO, "Kascommittee", True),
                      (BOARD, "Board", True),
                      (ADMIN, "Administrators", True),
                      (COMCO, "Computer Committee", True),
                      (BOOKS, "Books Committee", True),
                      (BOOKBUYERS, "Book Buyers", True),
                      (KICKIN, "Kickin Committee", True),
                      (LENDERS, "Lenders Committee", True),
                      ]

        for committee in committees:
            if len(Committee.objects.filter(code=committee[0])) == 0:
                Committee.objects.create(name=committee[1], code=committee[0], active_member_committee=committee[2])
                print("added " + committee[1])
            if len(Group.objects.filter(name=committee[0])) == 0:
                Group.objects.create(name=committee[0])
                print("added GROUP FOR " + committee[1])

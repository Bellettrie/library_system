from django.contrib.auth.models import Group, Permission

from django.core.management.base import BaseCommand

from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):


        rights = Permission.objects.all()
        f = open("committees.csv", "r")
        str = ""
        firstLine = f.readline().replace("\n", "").split(",")[1:]
        count = 1


        committees = []
        for com in firstLine:
            if com != "":
                committees.append(Committee.objects.get(code=com))

        groups = []
        for committee in committees:
            groups.append(Group.objects.get(name=committee.code))

        while True:
            line = f.readline()
            if not line:
                break
            line = line.replace("\n","").split(",")
            perm = line[0]
            codes = line[1:]
            print(perm)
            permission = Permission.objects.get(codename=perm)
            counter = 0
            for code in codes:
                if code=="0":
                    groups[counter].permissions.remove(permission)
                else:
                    groups[counter].permissions.add(permission)
                counter += 1

        for group in groups:
            group.save()
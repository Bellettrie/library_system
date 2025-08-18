from django.contrib.auth.models import Group, Permission

from django.core.management.base import BaseCommand

from members.models import Committee


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        committees = list(Committee.objects.all())

        rights = Permission.objects.all()
        f = open("committees.csv", "w")
        str = ""
        for committee in committees:
            str = str + "," + committee.code
        f.write(str + "\n")
        for right in rights:
            str = ""
            for committee in committees:
                group = Group.objects.get(name=committee.code)
                if right in group.permissions.all():
                    str = str + ",1"
                else:
                    str = str + ",0"
            f.write(right.codename + str + "\n")
            print(right.codename + str)
        f.close()

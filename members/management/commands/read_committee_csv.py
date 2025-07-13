from django.contrib.auth.models import Group, Permission

from django.core.management.base import BaseCommand

from members.models import Committee


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        f = open("committees.csv", "r")
        firstLine = f.readline().replace("\n", "").split(",")[1:]

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
            line = line.replace("\n", "").split(",")
            perm = line[0]
            codes = line[1:]
            print(perm)
            try:
                permission = Permission.objects.get(codename=perm)
            except Permission.DoesNotExist:
                continue
            counter = 0
            for code in codes:
                if code == "0":
                    groups[counter].permissions.remove(permission)
                else:
                    groups[counter].permissions.add(permission)
                counter += 1

        for group in groups:
            group.save()

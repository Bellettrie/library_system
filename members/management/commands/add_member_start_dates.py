from datetime import datetime, date

from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand
from members.models import Committee, Member, MembershipPeriod, MemberBackground, MembershipType
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from django.db import connection


def mig():
    from bellettrie_library_system.settings_migration import migration_database
    from django.conf import settings
    if not settings.SHOULD_MIGRATE:
        return
    mycursor = migration_database.cursor(dictionary=True)
    MembershipPeriod.objects.all().delete()
    mycursor.execute("SELECT * FROM klant_archief order by aangemaakt_op")
    for member in Member.objects.all():

        with connection.cursor() as cursor:
            cursor.execute("SELECT start_date, end_date, member_background_id, membership_type_id  FROM members_member WHERE id=" + str(member.id))

            a = cursor.fetchone()
            start_date = a[0]
            end_date = a[1]
            member_background_id = a[2]
            membership_type_id = a[3]
            if start_date and end_date:
                MembershipPeriod.objects.create(member=member, start_date=start_date, end_date=end_date, member_background_id=member_background_id,
                                                membership_type_id=membership_type_id)
            elif start_date:
                MembershipPeriod.objects.create(member=member, start_date=start_date, member_background_id=member_background_id,
                                                membership_type_id=membership_type_id)

    for x in mycursor:
        members = Member.objects.filter(old_id=x.get("klantnummer"))
        if len(members) == 0:
            continue
        member = members[0]

        start = (x.get("aangemaakt_op") or datetime.fromisoformat("1997-01-01")).date()
        end = (x.get("vervangen_op") or datetime.fromisoformat("2100-01-01")).date()

        r = x.get("einde") or (datetime.fromisoformat("2100-01-01").date())
        if (z := r) < end:
            end = z
        mc = MembershipPeriod.objects.create(member=member, start_date=start, end_date=end)

        try:
            m = MemberBackground.objects.get(old_str=x.get("herkomst"))
            mc.member_background = m
        except MemberBackground.DoesNotExist:
            print(x.get("herkomst"))
        try:
            m = MembershipType.objects.get(old_str=x.get("lidsoort"))
            mc.membership_type = m
        except MembershipType.DoesNotExist:
            print(x.get("lidsoort"))
        try:
            mc.save()
        except ValueError:
            print("ERROR")
    while True:
        deleted = set()

        for member in Member.objects.all():
            for msp in MembershipPeriod.objects.filter(member=member):
                for msp2 in MembershipPeriod.objects.filter(member=member, membership_type=msp.membership_type, member_background=msp.member_background):
                    if msp not in deleted and msp != msp2 and msp2 not in deleted:
                        start1 = (msp.start_date or datetime.fromisoformat("1900-01-01").date())
                        end1 = (msp.end_date or datetime.fromisoformat("2100-01-01").date())
                        start2 = (msp2.start_date or datetime.fromisoformat("1900-01-01").date())
                        end2 = (msp2.end_date or datetime.fromisoformat("2100-01-01").date())
                        if (start1 - end2).days <= 1 and (
                                start2 - end1).days <= 1:
                            msp.start_date = min(start1, start2)
                            msp.end_date = max(end1, end2)
                            msp.save()
                            deleted.add(msp2)
        print(deleted)
        for z in deleted:
            print(z, "A")
            z.delete()
        if len(deleted) == 0:
            break


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        mig()

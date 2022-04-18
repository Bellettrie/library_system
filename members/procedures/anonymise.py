from datetime import datetime, timedelta

from lendings.models import Lending
from members.exceptions import AnonymisationException
from members.models import MembershipPeriod
from members.models import Member


def set_member_reference_to_anonymous(filter_list, field, anonymous_members, dry_run):
    import random
    for z in filter_list:
        setattr(z, field, random.sample(anonymous_members, 1)[0])
        if not dry_run:
            z.save()


def anonymise_member(member: Member, dry_run=True):
    anonymous_members = list(Member.objects.filter(is_anonymous_user=True))
    from mail.models import MailLog
    from lendings.models import Lending
    set_member_reference_to_anonymous(Lending.objects.filter(member=member), 'member', anonymous_members, dry_run)
    set_member_reference_to_anonymous(Lending.objects.filter(lended_by=member), 'lended_by', anonymous_members, dry_run)
    set_member_reference_to_anonymous(Lending.objects.filter(handed_in_by=member), 'handed_in_by', anonymous_members,
                                      dry_run)

    from reservations.models import Reservation
    set_member_reference_to_anonymous(Reservation.objects.filter(member=member), 'member', anonymous_members, dry_run)
    set_member_reference_to_anonymous(Reservation.objects.filter(reserved_by=member), 'reserved_by', anonymous_members,
                                      dry_run)
    set_member_reference_to_anonymous(MailLog.objects.filter(member=member), 'member', anonymous_members, dry_run)
    set_member_reference_to_anonymous(MembershipPeriod.objects.filter(member=member), 'member', anonymous_members,
                                      dry_run)
    if not dry_run:
        member.is_anonimysed = True
        member.addressLineOne = "-"
        member.addressLineTwo = "-"
        member.addressLineThree = "-"
        member.addressLineFour = "-"
        member.student_number = "-"
        member.old_customer_type = None
        member.notes = "-"
        member.old_id = None
        member.membership_type_old = "-"
        member.phone = "-"
        member.save()


def anonymise_except(member: Member, current_date: datetime.date) -> None:
    """
    :param member: member to be anonymised
    :param current_date: date to use to calculate anonymisation (== today)
    :return: None
    :except ...: Raise exception if ...
    """
    if member.is_anonimysed:
        raise AnonymisationException("Already anonymised")
    if member.is_blacklisted:
        raise AnonymisationException("Is blacklisted")
    if member.is_currently_member():
        raise AnonymisationException("Is currently a member")
    if member.is_active():
        raise AnonymisationException("Member is still active")
    if member.user is not None and (member.user.last_login.date() - current_date).days < -400:
        raise AnonymisationException("Logged in recently;  will be anonymised in " + str(
            400 - (member.user.last_login.date() - current_date).days) + " days.")
    if (current_date - member.last_end_date()).days < 800:
        raise AnonymisationException("Was recently a member; can be anonymised in " + str(
            800 - (current_date - member.last_end_date()).days) + " days.")
    if len(Lending.objects.filter(member=member, handed_in=False)) > 0:
        raise AnonymisationException("Still has a book lent.")
    a = current_date - timedelta(days=180)
    if len(Lending.objects.filter(member=member, handed_in_on__gte=a)) > 0:
        raise AnonymisationException("Recently lent a book")
    from reservations.models import Reservation
    if len(Reservation.objects.filter(member=member)) > 0:
        raise AnonymisationException("Still has a reservation")


def can_be_anonymised(member: Member, current_date: datetime.date) -> bool:
    try:
        anonymise_except(member, current_date)
        return True
    except AnonymisationException:
        return False


def anonymise_or_except(member: Member, current_date: datetime.date, dry_run=True):
    anonymise_except(member, current_date)
    anonymise_member(member, dry_run)

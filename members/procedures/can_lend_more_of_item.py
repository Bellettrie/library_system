from members.models import Member
from utils.time import get_now


def can_lend_more_of_item(member: Member, item, from_reservation=False):
    from lendings.models import Lending
    from reservations.models import Reservation

    lendings = Lending.objects.filter(member=member,
                                      item__location__category__item_type=item.location.category.item_type,
                                      handed_in=False)
    reservations = Reservation.objects.filter(member=member,
                                              reservation_end_date__gt=get_now()) | Reservation.objects.filter(
        member=member, reservation_end_date__isnull=True)
    from config.models import LendingSettings
    fr = 0
    if from_reservation:
        fr = 1
    return (len(lendings) + len(reservations) - fr) < LendingSettings.get_for(item, member).max_count

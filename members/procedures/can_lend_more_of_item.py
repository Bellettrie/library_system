from datetime import datetime

from members.models import Member


def can_lend_more_of_item(member: Member, item):
    from lendings.models import Lending
    from reservations.models import Reservation

    lendings = Lending.objects.filter(member=member,
                                      item__location__category__item_type=item.location.category.item_type,
                                      handed_in=False)
    reservations = Reservation.objects.filter(member=member,
                                              reservation_end_date__gt=datetime.now()) | Reservation.objects.filter(
        member=member, reservation_end_date__isnull=True)
    from config.models import LendingSettings
    return (len(lendings) + len(reservations)) < LendingSettings.get_for(item, member).max_count
from lendings.models import Lending
from reservations.models import Reservation
from works.models import Item, Publication


class Row:
    def __init__(self):
        self.table = None

    def get_item(self) -> Item:
        raise NotImplementedError()

    def is_item(self):
        return True


class ItemRow(Row):
    def __init__(self, item: Item):
        super().__init__()
        self.item = item

    def get_item(self) -> Item:
        return self.item


class NoItemRow(Row):
    def __init__(self, publication: Publication):
        super().__init__()
        self.publication = publication

    def get_item(self) -> Item:
        return Item(publication=self.publication)

    def is_item(self):
        return False


class LendingRow(Row):
    def __init__(self, lending: Lending):
        super().__init__()
        self.lending = lending

    def get_item(self) -> Item:
        return self.lending.item


class ReservationRow(Row):
    def __init__(self, reservation: Reservation):
        super().__init__()
        self.reservation = reservation

    def get_item(self) -> Item:
        return self.reservation.item

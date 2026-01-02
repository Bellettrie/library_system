from django.db import models
from django.db.models import PROTECT
from django.shortcuts import get_object_or_404

from book_code_generation.models import BookCode
from inventarisation.models import Inventarisation
from lendings.models import Lending
from reservations.models import Reservation
from utils.time import get_now
from works.models.abstract import NamedThing
from works.models.location import Location
from works.models.work import Work


class Item(NamedThing, BookCode):
    old_id = models.IntegerField(null=True)
    location = models.ForeignKey(Location, on_delete=PROTECT)
    publication = models.ForeignKey(Work, on_delete=PROTECT)
    isbn10 = models.CharField(max_length=64, null=True, blank=True)
    isbn13 = models.CharField(max_length=64, null=True, blank=True)
    pages = models.CharField(null=True, blank=True, max_length=32)
    hidden = models.BooleanField()
    comment = models.TextField(default='', null=True, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    bought_date = models.DateField(default="1900-01-01", null=True, blank=True)
    added_on = models.DateField(auto_now_add=True)
    last_seen = models.DateField(null=True, blank=True)
    book_code_extension = models.CharField(max_length=16, blank=True, db_index=True)  # Where in the library is it?

    def get_recode(self):
        from recode.models import Recode
        recode = Recode.objects.filter(item_id=self.id)
        if len(recode) == 1:
            return recode[0]
        else:
            return None

    def display_code(self):
        return self.book_code + " " + self.book_code_extension

    def in_available_state(self):
        return self.get_state().state.is_available

    def is_lent_out(self):
        return Lending.objects.filter(item_id=self.id, handed_in=False).count() > 0

    def is_available_for_lending(self):
        return self.in_available_state() and not self.is_lent_out()

    def is_reserved(self):
        reservations = Reservation.objects.filter(item_id=self.id)
        return reservations.count() > 0

    def is_available_for_reservation(self):
        return self.in_available_state() and not self.is_reserved()

    def is_reserved_for(self, member):
        reservations = Reservation.objects.filter(item_id=self.id, member=member)
        return reservations.count() > 0

    def current_lending_or_404(self):
        return get_object_or_404(Lending, item_id=self.id, handed_in=False)

    def current_lending(self):
        lndngs = Lending.objects.filter(item_id=self.id, handed_in=False)
        if len(lndngs) != 1:
            return None
        return lndngs[0]

    def get_title(self):
        return self.title or self.publication.title

    def get_article(self):
        return self.article or self.publication.article

    def get_sub_title(self):
        return self.sub_title or self.publication.sub_title

    def get_language(self):
        return self.language or self.publication.language

    def get_original_title(self):
        return self.publication.original_title

    def get_original_sub_title(self):
        return self.publication.original_subtitle

    def get_original_article(self):
        return self.publication.original_article

    def get_original_language(self):
        return self.publication.original_language

    def get_state(self):
        from works.models.item_state import ItemState
        states = ItemState.objects.filter(item_id=self.id).order_by("-date_time")
        if len(states) == 0:
            return ItemState(item_id=self.id, date_time=get_now(), type="AVAILABLE")
        return states[0]

    def get_prev_state(self):
        from works.models.item_state import ItemState

        states = ItemState.objects.filter(item_id=self.id).order_by("-date_time")
        if len(states) <= 1:
            return ItemState(item_id=self.id, date_time=get_now(), type="AVAILABLE")
        return states[1]

    def get_most_recent_state_not_this_inventarisation(self, inventarisation: Inventarisation):
        from works.models.item_state import ItemState

        states = ItemState.objects.filter(item_id=self.id).exclude(inventarisation=inventarisation).order_by(
            "-date_time")
        if len(states) == 0:
            return ItemState(item_id=self.id, date_time=get_now(), type="AVAILABLE")
        return states[0]

    def is_seen(self, reason):
        from works.models.item_state import ItemState, get_state
        state = self.get_state()
        if state.type != "AVAILABLE":
            state_type = get_state(state.type)
            if state_type.next_yes_state_name == "AVAILABLE":
                ItemState.objects.create(item_id=self.id, type="AVAILABLE",
                                         reason="Automatically switched because of reason: " + reason)

    def generate_code_full(self):
        return self.publication.generate_code_full(self.location)

    def generate_code_prefix(self):
        return self.publication.generate_code_prefix(self.location)

    def get_isbn10(self):
        if self.isbn10 is not None:
            return self.isbn10
        else:
            return ''

    def get_isbn13(self):
        if self.isbn13 is not None:
            return self.isbn13
        else:
            return ''

    def get_pages(self):
        if self.pages is not None:
            return self.pages
        else:
            return ''

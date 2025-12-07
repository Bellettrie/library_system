from asyncio import Protocol

from django.db.models import QuerySet

from search.procedures.search_query.filters import StatesFilter
from works.models import Work
from works.models.item_state import get_available_states


class ResultBase(Protocol):
    def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
        pass


class ItemsOnly(ResultBase):
    def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
        return query.filter(itemid__isnull=False)


class AvailableItemsOnly(ResultBase):
    def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
        statz = get_available_states()
        sf = StatesFilter(list(map(lambda state: state.state_name, statz)))
        query = sf.filter(query)
        return ItemsOnly().finish_query(query)


class AllWorks(ResultBase):
    def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
        return query

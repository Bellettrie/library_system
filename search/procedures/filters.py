from django.db.models.expressions import RawSQL


class SearchFilter:
    def filter(self, query):
        return query
    def order (self, query):
        return query

class TextSearchFilter(SearchFilter):
    def __init__(self, query):
        self.query = query

    def filter(self, query):
        txt = self.query.lower()
        return query.annotate(
            rank=RawSQL("ts_rank(all_text_search_vector, websearch_to_tsquery('simple', %s))*result_priority", [txt]),
        ).extra(where=["websearch_to_tsquery('simple', %s) @@ all_text_search_vector"], params=[txt])
    def order (self, query):
        return query.order_by('-rank')

class HiddenFilter(SearchFilter):
    def __init__(self, with_hidden: bool):
        self.with_hidden = with_hidden

    def filter(self, query):
        return query.filter(hidden=self.with_hidden)

    def order (self, query):
        return query
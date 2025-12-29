from django_components import Component, register

from works.components.works.table.row import Row
from works.models import Item
from works.models.row_data import RowData


@register("works.table.Card")
class Card(Row):
    template_name = "works/table/card.html"

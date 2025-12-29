from typing import List

from django.urls import reverse
from django_components import Component, register, types

from works.components.works.table.row_base import RowBase
from works.models import Item
from works.models.row_data import RowData


@register("works.table.Row")
class Row(RowBase):
    def get_context_data(self, *args, skip_header: bool = False, **kwargs):
        ctx_data = super(Row, self).get_context_data(*args, **kwargs)
        ctx_data['skip_header'] = skip_header
        return ctx_data

    # Renders a table row for a single item.
    # all_authors is used to tell the table to show more than one author for each item (if more are linked)
    # skip_header is used to tell the row to not render the item code column.
    template_name = "works/table/row.html"

from typing import List

from tables.columns import Column
from tables.rows import Row


class Table:
    def __init__(self, rows: List[Row], columns: List[Column], display_subworks=False):
        self.rows = rows
        self.columns = columns
        self.display_subworks = display_subworks

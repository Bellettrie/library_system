from typing import List

from tables.columns import Column
from tables.rows import Row


class Table:
    def __init__(self, rows: List[Row], columns: List[Column]):
        self.rows = rows
        self.columns = columns

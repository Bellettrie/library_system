class RowData:
    def __init__(self, item=None, work=None, series=None):
        self.item = item
        self.work = work
        self.series = series

    def get_item(self):
        if self.item:
            return self.item
        return None

    def get_work(self):
        if self.work:
            return self.work
        if self.item:
            return self.item.work
        if self.series:
            return self.series.work

    def get_series(self):
        if self.series:
            return self.series.series
        if self.work:
            sr = self.work.as_series()
            return sr
        return None

    def get_book_code(self):
        if self.item:
            return self.item.book_code, self.item.book_code_extension
        elif self.series:
            return self.series.book_code, ""
        elif self.work.as_series():
            return self.work.as_series().book_code, ""
        return "", ""

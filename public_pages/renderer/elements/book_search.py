from public_pages.renderer.elements.area import Area


class BookSearch(Area):
    def __init__(self, **kwargs):
        super().__init__()
        self.ctx["layout_type"] = "search"

    def add_block(self, block):
        raise Exception("Cannot add elements to book search")

    def does_blocks(self):
        return False

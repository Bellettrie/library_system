from public_pages.renderer.elements.base import Base, Area


class BookSearch(Area):
    template="public_pages/elems/search_field.html"
    allowed_context_keys = ["layout_overrides"]
    def add_block(self, block):
        raise Exception("Cannot add elements to book search")

    def does_blocks(self):
        return False
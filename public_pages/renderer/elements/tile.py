from public_pages.renderer.elements.area import Area


class Tile(Area):
    def __init__(self, **kwargs):
        super().__init__()
        self.add_to_context("layout_type", "tile")

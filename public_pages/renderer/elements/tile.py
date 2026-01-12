from public_pages.renderer.elements.area import Area
from public_pages.renderer.elements.base import Base


class Tile(Area):
    allowed_context_keys = Base.allowed_context_keys + ["title", "layout_type", "image_path", "image_alt"]

    template = "public_pages/elems/tile.html"

    def __init__(self, **kwargs):
        super().__init__()
        self.add_to_context("layout_type", "tile")

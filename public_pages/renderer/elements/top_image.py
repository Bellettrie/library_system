from public_pages.renderer.elements.area import Area
from public_pages.renderer.elements.base import Base
from public_pages.renderer.elements.tile import Tile


class TopImage(Tile):
    template = "public_pages/elems/tile_top_image.html"
    allowed_context_keys = Base.allowed_context_keys + ["title", "layout_type", "image_path", "image_alt", "image_top"]

    def __init__(self, **kwargs):
        super().__init__()
        self.add_to_context("layout_type", "tile")
        self.add_to_context("image_top", True)

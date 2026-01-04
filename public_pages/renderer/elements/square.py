from public_pages.renderer.elements.base import Area


class Square(Area):
    template = "public_pages/elems/square.html"
    allowed_context_keys = ["layout_overrides", "image_path", "image_alt", "title"]

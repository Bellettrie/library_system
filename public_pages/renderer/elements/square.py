from public_pages.renderer.elements.base import Base


class Square(Base):
    template="public_pages/elems/square.html"
    allowed_context_keys = ["layout_overrides", "image_path", "image_alt", "title"]



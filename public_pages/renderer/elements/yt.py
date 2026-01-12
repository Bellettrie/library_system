from django.template.loader import get_template

from public_pages.renderer.elements.base import Base
from public_pages.renderer.elements.area import Area


class YT(Area):
    allowed_context_keys = Base.allowed_context_keys + ["url"]
    def __init__(self, **kwargs):
        super().__init__()
        self.ctx["layout_type"] = "yt"

    def add_line(self, line):
        if line.strip():
            if self.ctx.get("url", "") != "":
                raise Exception("YT elements must have exactly one video url")
            self.add_to_context("url", line.strip())
            return self
        return self

    def render(self):
        if self.ctx.get("url", "") == "":
            raise Exception("YT elements must have a video url")
        return super().render()

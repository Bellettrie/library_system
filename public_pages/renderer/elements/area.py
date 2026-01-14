from django.template.loader import get_template

from public_pages.renderer.elements.base import Base
from public_pages.renderer.elements.blocks.line_block import LineBlock


class Area(Base):
    allowed_context_keys = Base.allowed_context_keys + ["title", "layout_type"]
    template = "public_pages/elems/area.html"

    def __init__(self, always_render=True):
        super().__init__(always_render)
        self.blocks = [LineBlock()]

    def add_line(self, line: str):
        if len(line.strip()) > 0:
            self.should_render = True

        block = self.blocks[-1]
        if hasattr(block, "is_end_line") and block.is_end_line(line):
            self.blocks.append(LineBlock())
            return self

        self.blocks[-1].add_line(line)
        return self

    def add_block(self, block):
        self.blocks.append(block)
        self.should_render = True
        return self

    def current_block(self):
        return self.blocks[-1]

    def does_blocks(self):
        return True

    def render(self):
        if not self.should_render:
            return ""
        html = ""
        for block in self.blocks:
            html += block.render()

        search_template = get_template(self.template)
        ctx = self.ctx.copy()
        ctx["content"] = html
        ctx["title"] = self.ctx.get("title", "")
        ctx["layout"] = self.ctx.get("layout_overrides", "")

        return search_template.render(context=ctx)

from typing import Any

from django.template.loader import get_template

from public_pages.renderer.elements.blocks.line_block import LineBlock


class Base:
    template="public_pages/elems/base_area.html"
    allowed_context_keys=["layout_overrides", "title"]

    def __init__(self, should_render=True):
        self.should_render = should_render
        self.blocks = [LineBlock()]
        self.ctx = {
            "layout_overrides": "w-full md:flex-1",
        }


    def add_line(self, line: str):
        if len(line.strip())>0:
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

    def add_to_context(self, ky: str, value: Any):
        if ky in self.allowed_context_keys:
            self.ctx[ky]= value
        else:
            raise Exception(f"The key {ky} is not allowed for type {type(self)}")
        return self

    def render(self):
        if  not self.should_render:
            return ""

        html = ""
        for block in self.blocks:
            html += block.render()

        search_template = get_template(self.template)
        return search_template.render(context={"content": html, "title":self.ctx.get("title", ""), "layout": self.ctx.get("layout_overrides", ""), 'ctx':self.ctx})

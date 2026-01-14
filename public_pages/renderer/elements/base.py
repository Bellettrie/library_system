from typing import Any

from django.template.loader import get_template


class Base:
    template = "abstract"
    allowed_context_keys = ["layout_overrides", "title"]

    def __init__(self, should_render=True):
        self.should_render = should_render
        self.ctx = {
            "layout_overrides": "w-full md:flex-1",
        }

    def add_line(self, line):
        if len(line.strip()) == 0:
            return
        raise Exception(f"Cannot add line to {type(self)}. Line: {line}")

    def add_block(self, block):
        raise Exception(f"Cannot add elements to {type(self)}")

    def current_block(self):
        raise Exception(f"Cannot get current block from {type(self)}")

    def does_blocks(self):
        return False

    def add_to_context(self, ky: str, value: Any):
        if ky in self.allowed_context_keys:
            self.ctx[ky] = value
        else:
            typ = str(type(self))
            err_str = f"The key {ky} is not allowed for type {typ}"
            raise Exception(err_str)
        return self

    def render(self):
        if self.template == "abstract":
            raise Exception("Cannot render abstract block")

        search_template = get_template(self.template)
        return search_template.render(context={"ctx": self.ctx})

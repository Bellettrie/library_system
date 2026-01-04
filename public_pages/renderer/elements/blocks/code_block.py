from django.template.loader import get_template

from public_pages.renderer.elements.base import Base


class CodeBlock:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lines = []

    template="public_pages/elems/code_block.html"
    allowed_context_keys = ["layout_overrides"]
    def add_line(self, line):
        self.lines.append(line)

    def render(self):
        search_template = get_template(self.template)
        return search_template.render(context={"lines":self.lines})

    def is_verbatim(self):
        return True
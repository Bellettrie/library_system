import markdown
from django.template.loader import get_template

from public_pages.renderer.django_markdown import DjangoUrlExtension, ProcessorExtension


class LineBlock:
    template = "public_pages/elems/prose.html"

    def __init__(self):
        self.lines = []

    def add_line(self, line):
        if line.strip() == "#!interrupt":
            return self
        self.lines.append(line)
        return self

    def render(self):
        markdown_text = ""
        for line in self.lines:
            markdown_text += line + "\n"
        md = markdown.Markdown(
            extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()])
        content = md.convert(markdown_text)
        search_template = get_template(self.template)
        return search_template.render(context={"content": content})

    def is_verbatim(self):
        return False

import markdown
from django.template.loader import get_template

from public_pages.renderer.django_markdown import ProcessorExtension, DjangoUrlExtension
from works.models import Work
from works.models.row_data import RowData


class WorkBlock:
    def __init__(self, work_id, *args, **kwargs):
        super().__init__()
        self.lines = []
        self.work = Work.objects.get(pk=work_id)

    template = "public_pages/elems/book_block.html"
    allowed_context_keys = ["layout_overrides"]

    def add_line(self, line):
        self.lines.append(line)

    def render(self):
        search_template = get_template(self.template)
        md = "\n".join(self.lines)

        proc = markdown.Markdown(
            extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()])

        row = RowData(work=self.work)
        return search_template.render(context={"row": row, "lines": proc.convert(md)})

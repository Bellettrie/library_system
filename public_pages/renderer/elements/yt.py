from django.template.loader import get_template

from public_pages.renderer.elements.base import Base


class YT(Base):
    template="public_pages/elems/yt.html"
    allowed_context_keys = ["layout_overrides"]
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url= ""

    def add_line(self, line):

        if line.strip():
            if self.url != "":
                raise Exception("YT elements must have exactly one video url")
            self.url = line.strip()
            return self
        return self

    def render(self):
        if self.url == "":
            raise Exception("YT elements must have a video url")
        search_template = get_template('public_pages/elems/yt.html')
        return search_template.render(context={"url": self.url, "layout": "w-96"})


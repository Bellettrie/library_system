import logging
import urllib

from django.conf import settings
from django.template.loader import get_template

from public_pages.renderer.elements.base import Base
from public_pages.renderer.elements.area import Area


# The render trafficlight function creates a trafficlight that shows whether the DK is open
def get_open():
    try:
        f = urllib.request.urlopen(settings.IS_OPEN_URL, timeout=120)
        is_open_result = str(f.read()).lower()
    except urllib.error.URLError as e:
        logging.error(e)
        return False
    return "true" in is_open_result


class TrafficLight(Area):
    allowed_context_keys = ["layout_overrides", "title"]

    def __init__(self, **kwargs):
        super(TrafficLight, self).__init__(**kwargs)
        self.ctx["layout_type"] = "traffic_light"
        self.ctx["title"] = "Are we open?"
        self.ctx["open"] = get_open()
        print("HERE")

    def add_line(self, line: str):
        if len(line.strip()) == 0:
            return self
        raise Exception("Cannot add text to traffic light")

import logging
import urllib

from django.conf import settings
from django.template.loader import get_template

from public_pages.renderer.elements.base import Base


# The render trafficlight function creates a trafficlight that shows whether the DK is open
def get_open():
    try:
        f = urllib.request.urlopen(settings.IS_OPEN_URL, timeout=120)
        is_open_result = str(f.read()).lower()
    except urllib.error.URLError as e:
        logging.error(e)
        return False
    return "true" in is_open_result


class TrafficLight(Base):
    template = "public_pages/elems/traffic_light.html"
    allowed_context_keys = ["layout_overrides"]

    def add_line(self, line: str):
        if len(line.strip()) == 0:
            return self
        raise Exception("Cannot add text to traffic light")

    def render(self):
        search_template = get_template('public_pages/elems/traffic_light.html')
        return search_template.render(context={"open": get_open(), "layout": "w-96"})

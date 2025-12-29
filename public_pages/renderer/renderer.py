import logging

import markdown
from django.conf import settings
from django.template.loader import get_template

from public_pages.renderer.django_markdown import DjangoUrlExtension, ProcessorExtension


# These functions are responsible for displaying parts of the webpages. These translate quite directly into bootstrap components
# The *_ is used to "eat" any unneeded parameters\

# The interrupt ends a bootstrap row component and starts a new one.
def render_interrupt(markdown_text: str, title: str, layout_overrides: str = "", *_):
    search_template = get_template('public_pages/elems/interrupt.html')
    return search_template.render(context={"content": markdown_text})


# Shows the youtube vid
def render_yt(markdown_text: str, title: str, layout_overrides: str = "", *_):
    yt_template = get_template('public_pages/elems/yt.html')
    return yt_template.render(context={"url": markdown_text})


# The base section creates a basic text area with a size. Observe that the title parameter is ignored, but it's kept to keep standardised functions.
def render_base_section(markdown_text: str, title: str, layout_overrides: str = "", *_):
    md = markdown.Markdown(extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()])
    html = md.convert(markdown_text)
    search_template = get_template('public_pages/elems/basic_area.html')
    return search_template.render(context={"content": html, "layout": layout_overrides})


# The render square function creates a bootstrap card component.
def render_square(markdown_text: str, title: str, layout_overrides: str = "", *_):
    md = markdown.Markdown(extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()])
    html = md.convert(markdown_text)
    search_template = get_template('public_pages/elems/square.html')
    return search_template.render(context={"content": html, "layout": layout_overrides, "title": title})


# The render find function creates a bootstrap card with a search field for finding books.
def render_find(markdown_text: str, title: str, layout_overrides: str = "", *_):
    md = markdown.Markdown(
        extensions=[DjangoUrlExtension(), 'tables', 'md_in_html', 'attr_list', ProcessorExtension()], )

    html = md.convert(markdown_text)
    search_template = get_template('public_pages/elems/search_field.html')
    return search_template.render(context={"content": html, "layout": layout_overrides})


# The render trafficlight function creates a trafficlight that shows whether the DK is open
def get_open():
    import urllib.request
    try:
        f = urllib.request.urlopen(settings.IS_OPEN_URL, timeout=120)
        is_open_result = str(f.read()).lower()
    except urllib.error.URLError as e:
        logging.error(e)
        return False
    return "true" in is_open_result


def render_trafficlight(markdown_text: str, title: str, layout_overrides: str = "", *_):
    search_template = get_template('public_pages/elems/traffic_light.html')
    return search_template.render(context={"open": get_open(), "layout": "w-96"})


def start_row(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '<div class="grow flex flex-col lg:flex-row gap-3 {layout}">'.format(layout=layout_overrides)


def end_row(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '</div>'


def start_column(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '<div class="grow flex flex-col gap-3 {layout}">'.format(layout=layout_overrides)


def end_column(markdown_text: str, title: str, layout_overrides: str = "", *_):
    return '</div>'


CMDS = {
    "base": render_base_section,
    "square": render_square,
    "search": render_find,
    "yt": render_yt,
    "light": render_trafficlight,
    "interrupt": render_interrupt,
    "start_row": start_row,
    "end_row": end_row,
    "start_column": start_column,
    "end_column": end_column,
}


def get_overrides() -> str:
    return "w-full md:flex-1"


# The render_md function is the main rendering function.
# It collects lines if they are not lines that start new components. If they are a line that starts a new component
# then the previous component is rendered, and a new one is started.
def render_md(markdown_text: str, show_errors: bool = False):
    try:
        return render(markdown_text)
    except Exception as e:
        if show_errors:
            return str(e)
        return "Could not load page, please contact the site's administrator."


def render(markdown_text):
    lines = ""
    result = ""
    title = ""
    cms = None
    first_line = True
    for line in markdown_text.split("\n"):
        # Set the title of the current component
        if line.startswith("#!title"):
            title = line[7:].strip()
        elif line.startswith("#!mdflex"):
            pass
        elif line.startswith("#!lgflex"):
            pass

        # new component barrier
        elif line.startswith("#!"):
            if not first_line:
                result += CMDS[cms[0]](lines, title, layout_overrides=get_overrides())
            cms = line[2:].strip().split(" ")
            # Basic sanity check: does the command exist at all
            if cms[0] not in CMDS.keys():
                return cms[0] + " : not a valid keyword"
            lines = ""
            title = ""
        else:
            lines += "\n" + line
        first_line = False
    # If no specific blocks are made, make a 12/12 block with *everything*
    if cms is None:
        cms = ["base"]
    result += CMDS[cms[0]](lines, title, layout_overrides=get_overrides())
    return result

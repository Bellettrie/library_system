import html

from public_pages.renderer.elements.base import Base
from public_pages.renderer.elements.area import Area
from public_pages.renderer.elements.blocks.book_block import WorkBlock
from public_pages.renderer.elements.blocks.code_block import CodeBlock
from public_pages.renderer.elements.blocks.line_block import LineBlock
from public_pages.renderer.elements.book_search import BookSearch
from public_pages.renderer.elements.row_cols import StartRow, End, StartColumn
from public_pages.renderer.elements.tile import Tile
from public_pages.renderer.elements.top_image import TopImage
from public_pages.renderer.elements.traffic_light import TrafficLight
from public_pages.renderer.elements.yt import YT


# The render_md function is the main rendering function.
# It collects lines if they are not lines that start new components. If they are a line that starts a new component
# then the previous component is rendered, and a new one is started.
def render_md(markdown_text: str, show_errors: bool = False):
    try:
        return render(markdown_text)
    except Exception as e:
        if show_errors:
            return html.escape(str(e))
        return "Could not load page, please contact the site's administrator."


def render(markdown_text):
    col = StartColumn()
    result = col.render()
    current_element = col.directly_next_element()

    for line in markdown_text.split("\n"):
        # Handle code block starts/ends in a way that still ends blocks even if in verbatim mode.
        if line.startswith("```"):
            if isinstance(current_element.current_block(), CodeBlock):
                current_element.add_block(LineBlock())
            else:
                current_element.add_block(CodeBlock())
            continue

        # Check whether the current block is verbatim.
        if current_element.does_blocks() and hasattr(current_element.current_block(),
                                                     "is_verbatim") and current_element.current_block().is_verbatim():
            current_element.add_line(line)
            continue

        lx = line.strip()
        if lx.startswith("#!"):
            previous_element = current_element
            current_element = handle_custom_keyword(previous_element, lx)

            # We should render the previous element if we have moved on to the next
            if previous_element != current_element:
                result += previous_element.render()
                # Sometimes we want to only quickly stay in a specific element, and directly move to the next
                # This is mostly for starting and ending rows/columns for now.
                if hasattr(current_element, "directly_next_element"):
                    result += current_element.render()
                    current_element = current_element.directly_next_element()
        else:
            current_element.add_line(lx)

    result += current_element.render()
    return result + End().render()


# We add some extra keywords to our markdown dialect
# They are defined here.
def handle_custom_keyword(current_element, ky) -> Base:
    blocks = {
        "base": register_element(Area),
        "area": register_element(Area),
        "square": register_element(Tile),
        "tile": register_element(Tile),
        "book_block": register_work,
        "line_block": register_line_block,
        "tile_top_image": register_element(TopImage),

        "search": register_element(BookSearch),
        "yt": register_element(YT),
        "light": register_element(TrafficLight),
        "start_row": register_element(StartRow),
        "end_row": register_element(End),
        "start_column": register_element(StartColumn),
        "end_column": register_element(End),
        "title": register_set_context_key("title"),
        "image": register_set_context_key("image_path"),
        "image_alt": register_set_context_key("image_alt"),
    }

    row = ky[2:].strip().split(" ")
    kyw = row[0].strip()
    cm = blocks.get(kyw, None)
    if not cm:
        raise Exception(f"No command: {kyw}")
    return cm(current_element, *row[1:])


def register_line_block(area):
    area.add_block(LineBlock())
    return area


def register_work(area, *args):
    area.add_block(WorkBlock(*args))
    return area


# Register elements that we want to render on the page
def register_element(class_of_element_to_create):
    def inner(*args):
        return class_of_element_to_create()

    return inner


# We also sometimes want to set specific values in the element we're working on.
# For instance, title.
def register_set_context_key(context_key):
    def inner(current_block, *context_values: str):
        current_block.add_to_context(context_key, " ".join(context_values).strip())
        return current_block

    return inner

from public_pages.renderer.elements.base import Base, Area


class StartRow(Base):
    def render(self):
        return '<div class="grow flex flex-col lg:flex-row gap-3 {layout}">'.format(
            layout=self.ctx.get("layout_overrides", ""))

    def add_line(self, line):
        if len(line.strip()) == 0:
            return
        raise Exception(f"Cannot add line to row start. Line: {line}")

    def add_block(self, block):
        raise Exception("Cannot add elements to row start")

    def directly_next_element(self):
        return Area(always_render=False)


class StartColumn(Base):
    def render(self):
        return '<div class="grow flex flex-col gap-3 {layout}">'.format(layout=self.ctx.get("layout_overrides", ""))

    def add_line(self, line):
        if len(line.strip()) == 0:
            return
        raise Exception(f"Cannot add line to column start. Line: {line}")

    def add_block(self, block):
        raise Exception("Cannot add elements to column start")

    def directly_next_element(self):
        return Area(always_render=False)


class End(Base):
    def render(self):
        return '</div>'

    def add_line(self, line):
        if len(line.strip()) == 0:
            return
        raise Exception(f"Cannot add line to end marker. Line: {line}")

    def add_block(self, block):
        raise Exception("Cannot add elements to end marker")

    def directly_next_element(self):
        return Area(always_render=False)

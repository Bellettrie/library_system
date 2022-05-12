from bellettrie_library_system.templatetags.paginator_tag import register
from tables.columns import Column
from tables.rows import Row


@register.simple_tag
def render_square(column: Column, row: Row, perms=None):
    return column.render(row, perms)

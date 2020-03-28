from django import template

register = template.Library()


@register.inclusion_tag('publication_table/publication_table.html')
def show_table(contents, perms, member=None):
    return {"contents": contents, "perms": perms, "member": member}


@register.inclusion_tag('publication_table/publication_table_row.html')
def show_row(book_result, is_even_row, perms, member):
    return {"publication": book_result.publication, "item_rows": book_result.item_rows, "item_options": book_result.item_options, "is_even_row": is_even_row,
            "is_single_item_row": len(book_result.item_rows) == 1, "perms": perms, "member": member}

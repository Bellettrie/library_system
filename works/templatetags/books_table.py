from django import template

from works.views import ItemRow

register = template.Library()


@register.inclusion_tag('publication_table/publication_table.html')
def show_table(contents, perms, user, member=None):
    return {"contents": contents, "perms": perms, "user": user, "member": member}


@register.inclusion_tag('publication_table/publication_table_row.html')
def show_row(book_result, is_even_row, perms, user, member):
    item_rows = []
    if book_result.item_rows is not None:
        item_rows = book_result.item_rows
    else:
        for item in book_result.publication.item_set.all():
            item_rows.append(ItemRow(item, book_result))
    return {"publication": book_result.publication, "item_rows": item_rows,
            "item_options": book_result.item_options, "is_even_row": is_even_row,
            "is_single_item_row": len(item_rows) == 1, "perms": perms, "user": user, "member": member}

from works.models import Item


def get_item_pages(inventarisation):
    items = Item.objects.filter(location=inventarisation.location).order_by('book_code_sortable')
    groups = []
    counter = 0

    for item in items:
        if counter == 0:
            groups.append([])
            counter = 10
        groups[len(groups) - 1].append(item)
        counter -= 1
    return groups

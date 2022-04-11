from django.test import TestCase
from works.models import Publication, Item, Category, Location, ItemType


def create_work(title: str):
    return Publication.objects.create(title=title,
                                      is_translated=False,
                                      date_added='1900-01-01',
                                      hidden=False,
                                      old_id=0
                                      )


def item_create(title: str, location: Location):
    work = create_work(title)
    return Item.objects.create(publication=work, location=location, hidden=False)


def location_create(location_name: str, category_name: str, item_type: ItemType):
    category = Category.objects.create(name=category_name, item_type=item_type)
    return Location.objects.create(name=location_name, category=category)

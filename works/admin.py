from django.contrib import admin

from works.models import ItemType, ItemState, Category, Location

# Register your models here.

admin.site.register(ItemType)
admin.site.register(ItemState)

admin.site.register(Category)
admin.site.register(Location)

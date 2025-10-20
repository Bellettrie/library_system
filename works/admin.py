from django.contrib import admin

from works.models import ItemType, ItemState, Category, Location, Work, SubWork, Publication

# Register your models here.

admin.site.register(ItemType)
admin.site.register(ItemState)

admin.site.register(Category)
admin.site.register(Location)


class AdminDta(admin.ModelAdmin):
    list_display = ('id', 'title', 'listed_author')
    search_fields = ['id', 'title', 'sub_title', 'original_title', 'original_subtitle', 'listed_author']
    search_help_text = "Super simple search"


admin.site.register(Work, AdminDta)
admin.site.register(SubWork, AdminDta)
admin.site.register(Publication, AdminDta)

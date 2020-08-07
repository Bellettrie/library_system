from django.contrib import admin

# Register your models here.
from public_pages.models import PublicPageGroup, PublicPage

admin.register(PublicPageGroup)
admin.register(PublicPage)
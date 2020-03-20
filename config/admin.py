from django.contrib import admin

# Register your models here.
from config.models import LendingSettings

admin.site.register(LendingSettings)
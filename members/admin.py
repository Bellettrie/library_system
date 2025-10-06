from django.contrib import admin

# Register your models here.
from members.models import Member, MemberBackground, MembershipType, Committee

admin.site.register(Member)
admin.site.register(MemberBackground)
admin.site.register(MembershipType)
admin.site.register(Committee)

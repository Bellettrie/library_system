from django.contrib import admin

# Register your models here.
from members.models import Member, MemberBackground, MembershipType

admin.site.register(Member)
admin.site.register(MemberBackground)
admin.site.register(MembershipType)

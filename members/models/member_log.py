from django.db import models
from django.db.models import SET_NULL

from members.models import MemberData
from members.models.member import Member


class MemberLog(MemberData):
    date_edited = models.DateTimeField(auto_now=True)
    member = models.ForeignKey(null=True, on_delete=SET_NULL, to=Member)

    @staticmethod
    def from_member(member: Member):
        data = MemberLog()
        data.member = member
        data.name = member.name
        data.nickname = member.nickname
        data.address_line_one = member.address_line_one
        data.address_line_two = member.address_line_two
        data.address_line_three = member.address_line_three
        data.address_line_four = member.address_line_four
        data.primary_email = member.primary_email
        data.secondary_email = member.secondary_email
        data.primary_email_in_use = member.primary_email_in_use
        data.secondary_email_in_use = member.secondary_email_in_use
        data.phone = member.phone
        data.student_number = member.student_number
        data.notes = member.notes
        data.save()

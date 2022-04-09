from django.db import models

from members.models import MemberData
from members.models.member import Member


class MemberLog(MemberData):
    date_edited = models.DateTimeField(auto_now=True)

    @staticmethod
    def from_member(member: Member):
        data = MemberLog()
        data.name = member.name
        data.nickname = member.nickname
        data.addressLineOne = member.addressLineOne
        data.addressLineTwo = member.addressLineTwo
        data.addressLineThree = member.addressLineThree
        data.addressLineFour = member.addressLineFour
        data.email = member.email
        data.phone = member.phone
        data.student_number = member.student_number
        # data.end_date = member.end_date
        data.notes = member.notes
        # data.start_date = member.start_date
        data.save()

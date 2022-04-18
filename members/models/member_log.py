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
        data.addressLineOne = member.addressLineOne
        data.addressLineTwo = member.addressLineTwo
        data.addressLineThree = member.addressLineThree
        data.addressLineFour = member.addressLineFour
        data.email = member.email
        data.phone = member.phone
        data.student_number = member.student_number
        data.notes = member.notes
        data.save()

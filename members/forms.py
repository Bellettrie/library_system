from django import forms
from django.forms import ModelForm

from members.models import Member


class EditForm(ModelForm):
    class Meta:
        model = Member
        fields = ['name',
                  'nickname',
                  'addressLineOne',
                  'addressLineTwo',
                  'addressLineThree',
                  'email',
                  'phone',
                  'student_number',
                  'notes',
                  'is_anonymous_user',
                  'end_date',
                  'user',
                  'committees',
                  ]
        labels = {'name': 'Name',
                  'nickname': 'Nickname',
                  'addressLineOne': 'Address',
                  'addressLineTwo': '',
                  'addressLineThree': '',
                  'email': 'E-mail',
                  'phone': 'Phone #',
                  'student_number': 'Student #',
                  'notes': 'Notes',
                  'is_anonymous_user': 'Is anonymous user',
                  'end_date': 'End date',
                  'user': 'User',
                  'committees': 'Committees',
                  }

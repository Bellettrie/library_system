from django import forms
from django.forms import ModelForm

from members.models import Member


class EditForm(ModelForm):
    def __init__(self, can_edit=False, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        if not can_edit:
            self.fields['committees'].widget.attrs['readonly'] = True

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
                  'member_background',
                  'membership_type',
                  'is_blacklisted'
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
                  'member_background': 'Member Background',
                  'membership_type': 'Membership Type',
                  'is_blacklisted': 'Is Blacklisted?'
                  }

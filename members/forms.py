from django import forms
from django.forms import ModelForm

from members.models import Member, MembershipPeriod


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
                  'dms_registered',
                  'committees',
                  'is_blacklisted',
                  'privacy_activities',
                  'privacy_publications',
                  'privacy_reunions',
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
                  'dms_registered': 'Is registered in DMS',
                  'committees': 'Committees',
                  'is_blacklisted': 'Is Blacklisted?',
                  'privacy_activities': 'Mails for Activities?',
                  'privacy_publications': 'Photos in Publications?',
                  'privacy_reunions': 'Mails for Reunions?'
                  }
        widgets = {
            'end_date': forms.DateInput(attrs={'class': 'datepicker'})
        }


class MembershipPeriodForm(ModelForm):
    class Meta:
        model = MembershipPeriod
        fields = ['member_background',
                  'membership_type',
                  'start_date',
                  'end_date']
        labels = {'member_background': 'Member Background',
                  'membership_type': 'Membership Type',
                  'start_date': 'Start Date',
                  'end_date': 'End Date'}
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'})
        }

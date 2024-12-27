from django import forms
from django.forms import ModelForm

from members.models import Member, MembershipPeriod


class EditForm(ModelForm):
    def __init__(self, can_edit=False, dms_edit=False, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        if not can_edit:
            self.fields['committees'].widget.attrs['readonly'] = True
            self.fields['committees'].widget = forms.MultipleHiddenInput()
        if not dms_edit:
            self.fields['dms_registered'].widget.attrs['disabled'] = True
        self.fields['is_anonymous_user'].widget = forms.HiddenInput()

    class Meta:
        model = Member
        fields = ['name',
                  'nickname',
                  'address_line_one',
                  'address_line_two',
                  'address_line_three',
                  'primary_email',
                  'primary_email_in_use',
                  'secondary_email',
                  'secondary_email_in_use',
                  'phone',
                  'student_number',
                  'privacy_activities',
                  'privacy_publications',
                  'privacy_reunions',
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
                  'address_line_one': 'Address',
                  'address_line_two': '',
                  'address_line_three': '',
                  'primary_email': 'Primary e-mail',
                  'primary_email_in_use': 'Primary e-mail in use',
                  'secondary_email': 'Secondary e-mail',
                  'secondary_email_in_use': 'Secondary e-mail in use',
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


class SignupForm(ModelForm):
    class Meta:
        model = Member
        fields = ['student_number',
                  'primary_email',
                  ]
        labels = {'student_number': 'Student Number',
                  'primary_email': 'Email Address'}

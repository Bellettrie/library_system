from django import forms


class EditForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    nickname = forms.CharField(label='Nickname', max_length=100)
    addressLineOne = forms.CharField(label='Adress', max_length=100)
    addressLineTwo = forms.CharField(label='', max_length=100)
    addressLineThree = forms.CharField(label='', max_length=100)
    email = forms.CharField(label='E-mail', max_length=100)
    phone = forms.CharField(label='Phone #', max_length=100)
    student_number = forms.CharField(label='Student #', max_length=100)
    notes = forms.CharField(label='Notes', max_length=100)
    is_anonymous_user = forms.BooleanField()
    end_date = forms.CharField(label='End date', max_length=100)


from django.forms import ModelForm
from book_code_generation.location_number_creation import CutterCodeRange


class EditForm(ModelForm):
    class Meta:
        model = CutterCodeRange
        fields = [
            'from_affix',
            'to_affix',
            'number',
            'generated_affix',
        ]

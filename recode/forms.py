from django.forms import ModelForm

from recode.models import Recode


class RecodeForm(ModelForm):
    class Meta:
        model = Recode
        fields = ['book_code', 'book_code_extension']

    def clean(self):
        cleaned_data = super().clean()
        book_code = cleaned_data.get("book_code")

        if len(book_code) == 0:
            msg = "Book Code cannot be empty"
            self.add_error("book_code", msg)

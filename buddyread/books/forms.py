from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from .models import Book, Review, BookClub


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author"]
        labels = {
            "title": "Titel",
            "author": "Auteur"
        }

    def validate_unique(self):
        pass

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Opslaan', css_class='btn-primary'))
    helper.form_method = 'POST'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["score", "comment"]
        labels = {
            "score": "Score",
            "comment": "Commentaar"
        }

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Opslaan', css_class='btn-primary'))
    helper.form_method = 'POST'


class BookClubForm(forms.ModelForm):
    class Meta:
        model = BookClub
        fields = ["name"]
        labels = {
            "name": "Naam",
        }

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Opslaan', css_class='btn-primary'))
    helper.form_method = 'POST'
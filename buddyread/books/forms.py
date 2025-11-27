from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Book, Review, BookClub


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author"]
        labels = {
            "title": "Titel",
            "author": "Auteur"
        }

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


class ConfirmDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Ik bevestig dat het bovenstaande onderdeel wordt verwijderd."
    )

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Verwijder', css_class='btn-danger'))
    helper.form_method = 'POST'


class ConfirmModeratorForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Ik bevestig dat bovenstaande lid beheerrechten krijgt."
    )

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Opslaan', css_class='btn-primary'))
    helper.form_method = 'POST'


class InviteMemberForm(forms.Form):

    username = forms.CharField(max_length=255, label="Gebruikersnaam")
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="Wachtwoord")
    password_repeat = forms.CharField(widget=forms.PasswordInput, required=False, label="Herhaal wachtwoord")

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Opslaan', css_class='btn-primary'))
    helper.form_method = 'POST'


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data["username"]

        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError('Er bestaat al een gebruiker met deze gebruikersnaam')

        password = cleaned_data["password"]
        password_repeat = cleaned_data["password_repeat"]
        if password != password_repeat:
            raise ValidationError('Het wachtwoord en de herhaling komen niet overeen')
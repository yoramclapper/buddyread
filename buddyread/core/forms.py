from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class ChangeAuthForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    username = forms.CharField(max_length=255, label="Gebruikersnaam")
    current_password = forms.CharField(widget=forms.PasswordInput, label="Huidig wachtwoord")
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Nieuw wachtwoord")
    new_password_repeat = forms.CharField(widget=forms.PasswordInput, required=False, label="Herhaal nieuw wachtwoord")

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Opslaan', css_class='btn-primary'))
    helper.form_method = 'POST'

    def clean_current_password(self):
        pwd = self.cleaned_data.get('current_password')
        if not self.user.check_password(pwd):
            raise ValidationError('Huidig wachtwoord is incorrect')
        return pwd

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data["new_password"]
        new_password_repeat = cleaned_data["new_password_repeat"]
        if new_password != new_password_repeat:
            raise ValidationError('Het nieuwe wachtwoord en de herhaling komen niet overeen')


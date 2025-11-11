from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

class ChangeAuthForm(forms.Form):
    username = forms.CharField(max_length=255, label="Gebruikersnaam")
    current_password = forms.CharField(widget=forms.PasswordInput, label="Huidig wachtwoord")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nieuw wachtwoord")
    new_password_repeat = forms.CharField(widget=forms.PasswordInput, label="Herhaal nieuw wachtwoord")

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Opslaan', css_class='btn-primary'))
    helper.form_method = 'POST'
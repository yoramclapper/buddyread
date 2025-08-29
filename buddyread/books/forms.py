from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from .models import Review

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
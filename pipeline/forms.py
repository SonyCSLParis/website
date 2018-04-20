from django import forms
from django.core.exceptions import ValidationError

#
# class InputForm(forms.Form):
#     input = forms.TextInput()
#
#     def clean_input(self):
#         data = self.cleaned_data['input']
#
#         # Check date is not in past.
#         if not data:
#             raise ValidationError("No input entered.")
#
#         return data

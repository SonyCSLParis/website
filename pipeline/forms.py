from django import forms


class InputForm(forms.Form):
    input = forms.Textarea()

    # def clean(self):
    #     cleaned_data = super(InputForm, self).clean()
    #     input = cleaned_data.get('input')
    #
    #     if not input:
    #         raise forms.ValidationError('No input provided.')

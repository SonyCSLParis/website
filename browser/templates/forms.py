from django import forms


class ComponentSearchForm(forms.Form):
    name = forms.CharField(max_length=30)
    description = forms.EmailField(max_length=254)
    source = forms.CharField(       # A hidden input for internal use
        max_length=50,              # tell from which page the user sent the message
        widget=forms.HiddenInput()
    )
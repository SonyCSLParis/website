from django import forms
from django import forms
from . import models
from django.contrib.admin.widgets import FilteredSelectMultiple


class PipelineForm(forms.Form):

    requests = forms.ModelMultipleChoiceField(queryset=models.PathRequest.objects.all(),
                                             label=(''),
                                             widget=FilteredSelectMultiple(
                                                 ('Requests'),
                                                 False,
                                             ))
    name = forms.CharField()
    description = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(PipelineForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'

    class Media:
        css = {
            'all': ('admin/css/widgets.css',),
        }
        # jsi18n is required by the widget
        js = ('/admin/jsi18n/',)

from django.db import models
from browser.models import Request, Parameter
from django.contrib import admin
from django import forms
import json
from django.template.defaultfilters import truncatechars


class Pipeline(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=200)
    requests = models.ManyToManyField(Request, related_name="multiple", null=True, blank=True)
    # used to assign pipes a number local to the pipeline. New pipes are given id_gen + 1 and id_gen is incremented.
    local_id_gen = models.IntegerField()


class Pipe(models.Model):

    pipe_line = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    run_time = models.DateTimeField(null=True, blank=True)  # time at which input was run
    output = models.TextField(null=True, blank=True)
    output_time = models.DateTimeField(null=True, blank=True)  # time at which output was acquired
    position = models.IntegerField()  # position in list of pipes used for ordering on page
    local_id = models.IntegerField()  # the id for the pipe locally also the id given to the output

    parameters = models.ManyToManyField(Parameter, related_name="has_params", null=True, blank=True)

    @property
    def short_output(self):
        return truncatechars(self.output, 500)

    def parameters_unpacked(self):
        return u'{parameters}'.format(parameters=self.parameters)


class PipeForm(forms.ModelForm):

    class Meta:
        model = Pipe
        fields = ['pipe_line', 'request', 'parameters', 'run_time', 'output', 'output_time', 'position', 'local_id']

    def clean_parameters(self):
        cleaned_data = super(PipeForm, self).clean()

        try:
            json_params = json.loads(cleaned_data['parameters'])
        except:
            return "Invalid JSON"

        return json_params

    def clean(self):
        cleaned_data = super(PipeForm, self).clean()

        return cleaned_data


class PipeAdmin(admin.ModelAdmin):
    list_display = ('pipe_line', 'request', 'run_time', 'position', 'local_id',
                    'short_output', 'output_time')
    form = PipeForm

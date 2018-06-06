from django.db import models
from component_browser.models import PathRequest, Parameter
from django.contrib import admin
from django import forms
import json
from django.template.defaultfilters import truncatechars


class Pipeline(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=200)
    requests = models.ManyToManyField(PathRequest, related_name="multiple", blank=True)
    # used to assign pipes a number local to the pipeline. New pipes are given id_gen + 1 and id_gen is incremented.
    local_id_gen = models.IntegerField(default=0)


class PipelineForm(forms.ModelForm):

    class Meta:
        model = Pipeline
        fields = ['name', 'description', 'requests', 'id']


class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'id')
    form = PipelineForm


class Pipe(models.Model):

    pipe_line = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    request = models.ForeignKey(PathRequest, on_delete=models.CASCADE)
    run_time = models.DateTimeField(null=True, blank=True)  # time at which input was run
    output = models.TextField(null=True, blank=True)
    output_time = models.DateTimeField(null=True, blank=True)  # time at which output was acquired
    position = models.IntegerField()  # position in list of pipes used for ordering on page
    local_id = models.IntegerField()  # the id for the pipe local to the pipeline

    parameters = models.ManyToManyField(Parameter, related_name="has_params", blank=True)

    @property
    def short_output(self):
        return truncatechars(self.output, 500)

    def parameters_unpacked(self):
        return u'{parameters}'.format(parameters=self.parameters)


class PipeForm(forms.ModelForm):

    class Meta:
        model = Pipe
        fields = ['pipe_line', 'request', 'id', 'parameters', 'run_time', 'output', 'output_time', 'position', 'local_id']

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
                    'short_output', 'output_time', 'id')
    form = PipeForm

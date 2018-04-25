from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib import admin
from django import forms
import json


class ComponentSpecification(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(max_length=200)
    host = models.URLField()
    base_path = models.TextField()


class Request(models.Model):

    def __str__(self):
        return '{} {}'.format(self.type, self.name)

    component = models.ForeignKey(ComponentSpecification, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()

    REQUEST_TYPES = (
        ("GET", 'GET'),
        ("POST", 'POST'),
        ("DELETE", 'DELETE'),
        ("PUT", 'PUT'),
        ("HEAD", 'HEAD'),
        ("OPTIONS", 'OPTIONS'),
        ("CONNECT", 'CONNECT'),
    )

    type = models.CharField(
        max_length=10,
        choices=REQUEST_TYPES
    )

    parameters = PickledObjectField(default={}, editable=True)

    def parameters_unpacked(self):
        return u'{parameters}'.format(parameters=self.parameters)

    path = models.TextField()


class RequestForm(forms.ModelForm):

    class Meta:
        model = Request
        fields = ['component', 'name', 'description', 'type', 'parameters', 'path']

    def clean_parameters(self):
         cleaned_data = super(RequestForm, self).clean()

         try:
             json_params = json.loads(cleaned_data['parameters'])
         except:
             return "Invalid JSON"

         return json_params

    def clean(self):
        cleaned_data = super(RequestForm, self).clean()

        return cleaned_data


class RequestAdmin(admin.ModelAdmin):
    list_display = ('component', 'name', 'description', 'type', 'parameters', 'path')
    list_editable = ('name', 'description', 'type', 'parameters', 'path')
    form = RequestForm


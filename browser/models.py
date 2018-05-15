from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib import admin
from django import forms
import json


class ComponentSpecification(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=200)
    host = models.URLField()
    base_path = models.TextField()
    title = models.TextField()
    version = models.TextField()
    openapi_version = models.TextField()


class Parameter(models.Model):

    def __str__(self):
        return self.name + str(self.pk)

    name = models.TextField()
    type = models.TextField()
    nested = models.ManyToManyField('self', related_name='sub_param', symmetrical=False) #
    example = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    enum = models.TextField(null=True, blank=True)
    required = models.TextField()
    default = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)


class ParameterForm(forms.ModelForm):

    class Meta:
        model = Parameter
        fields = ['name', 'type', 'example', 'description',  'enum', 'required', 'default', 'value']


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'example', 'description', 'enum', 'required', 'default', 'value')
    form = ParameterForm


class Request(models.Model):

    def __str__(self):
        return '{} {}'.format(self.type, self.name)

    component = models.ForeignKey(ComponentSpecification, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

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

    parameters = models.ManyToManyField(Parameter)

    def parameters_unpacked(self):
        return u'{parameters}'.format(parameters=self.parameters)

    path = models.TextField()


class RequestForm(forms.ModelForm):

    class Meta:
        model = Request
        fields = ['component', 'name', 'description', 'type', 'parameters', 'path']



class RequestAdmin(admin.ModelAdmin):
    list_display = ('component', 'name', 'description', 'type', 'path')
    form = RequestForm


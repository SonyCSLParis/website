from django.db import models
from django.contrib import admin
from django import forms


class ComponentSpecification(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=200)
    host = models.TextField()
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
    location = models.TextField(null=True, blank=True)  # can't use 'in'
    description = models.TextField(null=True, blank=True)
    enum = models.TextField(null=True, blank=True)
    required = models.TextField()
    default = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    format = models.TextField(null=True, blank=True)
    expression = models.TextField(null=True, blank=True)
    maximum = models.TextField(null=True, blank=True)
    minimum = models.TextField(null=True, blank=True)


class ParameterForm(forms.ModelForm):

    class Meta:
        model = Parameter
        fields = ['name', 'type', 'example', 'description',  'enum', 'required', 'default', 'value', 'expression']


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'example', 'description', 'enum', 'required', 'default', 'value', 'expression')
    form = ParameterForm


class PathRequest(models.Model):
    """
    Models a request made to a web service
    """
    def __str__(self):
        return '{} {}'.format(self.type, self.name)

    component = models.ForeignKey(ComponentSpecification, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

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

    responses = models.ManyToManyField('component_browser.PathResponse', related_name='ResponseTo')


class RequestForm(forms.ModelForm):

    class Meta:
        model = PathRequest
        fields = ['component', 'name', 'description', 'type', 'parameters', 'path']


class RequestAdmin(admin.ModelAdmin):
    list_display = ('component', 'name', 'description', 'type', 'path')
    form = RequestForm


class PathResponse(models.Model):
    """
    Models responses that might occur from making a request
    """

    request = models.ForeignKey('component_browser.PathRequest', on_delete=models.CASCADE)
    status_code = models.IntegerField()
    description = models.TextField()
    parameters = models.ManyToManyField(Parameter)

    def parameters_unpacked(self):
        return u'{parameters}'.format(parameters=self.parameters)


class PathResponseForm(forms.ModelForm):

    class Meta:
        model = PathResponse
        fields = ['status_code', 'description', 'request']


class PathFormAdmin(admin.ModelAdmin):
    list_display = ('status_code', 'description', 'request')
    form = PathResponseForm

from django.db import models


class ComponentSpecification(models.Model):

    def __str__(self):
        return self.component_name

    component_name = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(max_length=200)


class Request(models.Model):

    def __str__(self):
        return '{} {}'.format(self.request_type, self.request_name)

    component = models.ForeignKey(ComponentSpecification, on_delete=models.CASCADE)
    request_name = models.CharField(max_length=200)
    request_description = models.TextField()

    REQUEST_TYPES = (
        ("GET", 'GET'),
        ("POST", 'POST'),
        ("DELETE", 'DELETE'),
        ("PUT", 'PUT'),
        ("HEAD", 'HEAD'),
        ("OPTIONS", 'OPTIONS'),
        ("CONNECT", 'CONNECT'),
    )

    request_type = models.CharField(
        max_length=10,
        choices=REQUEST_TYPES
    )
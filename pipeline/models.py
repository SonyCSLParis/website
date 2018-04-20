from django.db import models
from browser.models import Request


class Pipeline(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=200)


class Pipe(models.Model):

    pipe_line = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    request = Request
    input = models.TextField(null=True, blank=True)
    run_time = models.DateTimeField(null=True, blank=True)  # time at which input was run
    output = models.TextField(null=True, blank=True)
    output_time = models.DateTimeField(null=True, blank=True)  # time at which output was acquired

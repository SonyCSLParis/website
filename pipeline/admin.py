from django.contrib import admin

from django.contrib import admin
from .models import Pipeline, Pipe

# Register models with the admin so they can be altered by admins
admin.site.register(Pipeline)
admin.site.register(Pipe)

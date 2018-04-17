from django.contrib import admin
from .models import Request, ComponentSpecification

# Register models with the admin so they can be altered by admins
admin.site.register(ComponentSpecification)
admin.site.register(Request)

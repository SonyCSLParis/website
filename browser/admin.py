from django.contrib import admin
from .models import PathRequest, ComponentSpecification, Parameter, ParameterAdmin, \
    RequestAdmin, PathResponse, PathFormAdmin

# Register models with the admin so they can be altered by admins
admin.site.register(ComponentSpecification)
admin.site.register(PathRequest, RequestAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(PathResponse, PathFormAdmin)

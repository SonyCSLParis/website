from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'upload'

urlpatterns = [
    path('', login_required(views.upload_file), name='upload_component'),
    ]

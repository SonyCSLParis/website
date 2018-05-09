"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
app_name = 'rest'

urlpatterns = [
    path('', views.external_request, name='request'),
    path('save_output', views.save_output, name='save_output'),
    path('save_input', views.save_input, name='save_input'),
    path('create_pipe', views.create_pipe, name='create_pipe'),
    path('delete_pipe', views.delete_pipe, name='delete_pipe'),
    path('move_up_pipe', views.move_up_pipe, name='move_up_pipe'),
    path('move_down_pipe', views.move_down_pipe, name='delete_pipe'),
    path('save_component', views.save_component, name='save_component')
    ]

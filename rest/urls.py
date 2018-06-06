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
    path('', views.get_output, name='rest'),
    path('run', views.run, name='run'),
    path('create_pipe', views.create_pipe, name='create_pipe'),
    path('delete_pipe', views.delete_pipe, name='delete_pipe'),
    path('move_up_pipe', views.move_up_pipe, name='move_up_pipe'),
    path('move_down_pipe', views.move_down_pipe, name='delete_pipe'),
    path('save_component', views.save_component, name='save_component'),
    path('get_output', views.get_output, name='get_output')
    ]

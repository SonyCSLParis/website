from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
app_name = 'pipeline'

urlpatterns = [
    path('', views.PipelinesFilterView.as_view(), name='index'),
    path('create_pipeline/', login_required(views.PipelineFormView.as_view()), name='create_pipeline'),
    path('<str:pk>/', views.PipelineView.as_view(), name='pipeline'),
    path('<str:pk>/output/<str:pipe_pk>', views.OutputDetailView.as_view(), name='output'),
    path('html_vis/<str:pipe_pk>', views.render_html, name='html_vis'),
    path('<str:pk>/input/<str:pipe_pk>', views.InputDetailView.as_view(), name='input'),
    path('<str:pk>/input_output/<str:pipe_pk>', views.InputOutputDetailView.as_view(), name='input_output'),
    path('<str:pk>/empty_pipe/', views.EmptyPipeView.as_view(), name='empty_pipe'),
    path('<str:pk>/run', views.run, name='run'),
    path('<str:pk>/create_pipe', views.create_pipe, name='create_pipe'),
    path('<str:pk>/delete_pipe', views.delete_pipe, name='delete_pipe'),
    path('<str:pk>/move_up_pipe', views.move_up_pipe, name='move_up_pipe'),
    path('<str:pk>/move_down_pipe', views.move_down_pipe, name='delete_pipe'),
    ]

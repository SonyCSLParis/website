from django.urls import path
from . import views
app_name = 'pipeline'

urlpatterns = [
    path('', views.PipelinesFilterView.as_view(), name='pipelines_index'),
    path('<str:pk>/', views.PipelineView.as_view(), name='pipeline'),
    path('output/<str:pk>', views.OutputDetailView.as_view(), name='output'),
    path('output', views.OutputDetailView.as_view(), name='output'),
    path('input/<str:pk>', views.InputDetailView.as_view(), name='input'),
    path('input', views.InputDetailView.as_view(), name='input'),
    path('input_output', views.InputOutputDetailView.as_view(), name='input_output'),
    path('input_output/<str:pipeline_pk>/<str:pipe_pk>', views.InputOutputDetailView.as_view(), name='input_output'),
    path('empty_pipeline/', views.EmptyPipeView.as_view(), name='empty_pipeline'),
    path('empty_pipeline/<str:pipeline_pk>/', views.EmptyPipeView.as_view(), name='empty_pipeline'),
    ]
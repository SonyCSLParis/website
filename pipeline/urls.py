from django.urls import path
from . import views
app_name = 'pipeline'

urlpatterns = [
    path('', views.PipelinesFilterView.as_view(), name='pipelines_index'),
    path('<str:pk>/', views.PipelineView.as_view(), name='pipeline'),
    path('<str>/output/<str:pk>', views.OutputDetailView.as_view(), name='output'),
    path('<str>/input/<str:pk>', views.OutputDetailView.as_view(), name='input'),
    ]

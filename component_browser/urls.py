from django.urls import path

from . import views
app_name = 'component_browser'

urlpatterns = [
    path('', views.ComponentFilterView.as_view(), name='index'),
    path('<str:pk>/', views.ComponentDetailView.as_view(), name='component'),
    path('request/<str:pk>/', views.RequestDetailView.as_view(), name='request'),
]


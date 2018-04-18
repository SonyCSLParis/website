from django.urls import path

from . import views
app_name = 'bench'

urlpatterns = [
    path('', views.ComponentFilterView.as_view(), name='index'),
    path('<str:pk>/', views.ComponentDetailView.as_view(), name='description'),
    path('request/<str:pk>/', views.RequestDetailView.as_view(), name='request'),
]


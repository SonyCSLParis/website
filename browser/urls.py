from django.urls import path

from . import views
app_name = 'bench'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:pk>/', views.DetailView.as_view(), name='description'),
    path('request/<str:pk>/', views.DetailView.as_view(), name='request')
]

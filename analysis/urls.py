from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('wait/<int:calc_id>/', views.wait, name='wait'),
    path('progress/<int:calc_id>/', views.progress, name='progress'),
    path('result/<int:calc_id>/', views.result, name='result'),
]
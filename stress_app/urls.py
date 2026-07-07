from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('webcam/', views.webcam, name='webcam'),
    path('predict_webcam/', views.predict_webcam, name='predict_webcam'),
]

from django.urls import path
from django_sendgrid_tracking import views

urlpatterns = [
    path('webhook', views.event_hooks, name='event_hooks'),
]

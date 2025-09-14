from django.urls import path
from . import views

urlpatterns = [
    path("", views.period_stats, name="period_stats"),
    path("goaldiff", views.goaldiff_stats, name="goaldiff_stats"),
]
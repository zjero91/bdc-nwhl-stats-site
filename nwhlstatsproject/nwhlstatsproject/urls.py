"""
URL configuration for nwhlstatsproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from stats_app.views.api import get_team_period, get_team_diff, get_shots_period, get_shots_diff

urlpatterns = [
    path("", include("stats_app.urls")),
    path("api/teams/period/", get_team_period, name='get_team_period'),
    path("api/teams/goaldiff/", get_team_diff, name="get_team_diff"),
    path("api/shots/period/", get_shots_period, name="get_shots_period"),
    path("api/shots/goaldiff/", get_shots_diff, name="get_shots_diff"),
    path('admin/', admin.site.urls),
]
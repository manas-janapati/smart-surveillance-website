"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from workers import views as worker_views
from workers import api as worker_api

urlpatterns = [
    # WORKER ENTRY POINT
    path("", worker_views.login_view, name="worker_login"),

    # WORKER PAGES
    path("home/", worker_views.home, name="worker_home"),
    path("survey/<int:survey_id>/", worker_views.survey_page, name="worker_survey"),
    path("profile/", worker_views.profile, name="worker_profile"),
    path("logout/", worker_views.logout_view, name="worker_logout"),

    # WORKER APIs
    path("api/surveys/", worker_api.surveys_api),
    path("api/survey/<int:survey_id>/", worker_api.survey_detail_api),

    # ADMIN
    path("admin/", admin.site.urls),
]

from django.urls import path
from . import views, api

urlpatterns = [
    path("", views.login_view, name="worker_login"),
    path("home/", views.home, name="worker_home"),
    path("survey/<int:survey_id>/", views.survey_page, name="worker_survey"),
    path("profile/", views.profile, name="worker_profile"),
    path("logout/", views.logout_view, name="worker_logout"),

    # APIs
    path("api/surveys/", api.surveys_api),
    path("api/survey/<int:survey_id>/", api.survey_detail_api),
]

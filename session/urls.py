from django.contrib import admin
from django.urls import path
from session.views import test_session_view


urlpatterns = [
    path("test-session/", test_session_view, name="test_session"),
]



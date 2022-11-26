"""ADDL URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include
from .flatpages import PrivacyPolicyView, TermsOfServiceView, IndexView


urlpatterns = [
   # path("__debug__/", include("debug_toolbar.urls")),
    # Flatpages
    path("", IndexView.as_view(), name="home"),
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy"),
    path("terms/", TermsOfServiceView.as_view(), name="terms"),
    # Django Pages
    path("accounts/", include("django.contrib.auth.urls"), name="Accounts"),
    path("admin/", admin.site.urls),
    # App Pages
    path("locations/", include("Locations.urls"), name="Locations"),
    path("members/", include("Members.urls"), name="Members"),
    path("schedule/", include("Schedule.urls"), name="Schedule"),
    path("scores/", include("Scores.urls"), name="Scores"),
    # API
    path("api/v1/", include("API.urls")),
]

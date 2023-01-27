from django.urls import path
from .flatpages import IndexView, PrivacyPolicyView, TermsOfServiceView

urlpatterns =[
    path("", IndexView.as_view(), name="home"),
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy"),
    path("terms/", TermsOfServiceView.as_view(), name="terms"),
]
from django.urls import path
from . import views

urlpatterns = [
    path('new/<str:pk>', views.ScoresheetCreateView, name='add_scoresheet'),
]
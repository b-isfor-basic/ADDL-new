from django.urls import path
from . import views

urlpatterns = [
    path('<str:pk>/add', views.ScoresheetCreateView, name='add_scoresheet'),
]
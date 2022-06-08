from django.urls import path
from . import views

urlpatterns = [
    path('add/<uuid:id>', views.ScoresheetCreateView, name='add_scoresheet'),
]
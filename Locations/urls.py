from django.urls import path
from . import views

urlpatterns = [
    path('', views.establishment_list, name='all_areas'),
    path('<int:pk>/', views.establishment_detail, name='area'),
    path('add_division/', views.create_division_form, name='create_division')
]

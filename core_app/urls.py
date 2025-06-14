# VOPS-Hub/core_app/urls.py
from django.urls import path
from . import views # Import views from the current app

app_name = 'core_app' # Namespace for URLs, useful for referencing them

urlpatterns = [
    # Path for listing all vessels
    path('vessels/', views.vessel_list, name='vessel_list'),
    # Path for showing a single vessel's details (using its primary key as an ID)
    path('vessels/<int:pk>/', views.vessel_detail, name='vessel_detail'),
]
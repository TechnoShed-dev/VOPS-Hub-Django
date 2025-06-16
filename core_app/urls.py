# VOPS-Hub/core_app/urls.py
from django.urls import path
from . import views # Import views from the current app

app_name = 'core_app' # Namespace for URLs, useful for referencing them

urlpatterns = [
    # Path for listing all vessels
    path('vessels/', views.vessel_list, name='vessel_list'),
    # Path for showing a single vessel's details (using its primary key as an ID)
    path('vessels/<int:pk>/', views.vessel_detail, name='vessel_detail'),
    # NEW: Path for adding a comment to a specific vessel
    path('vessels/<int:pk>/add_comment/', views.add_comment, name='add_comment'),
    path('comments/', views.comment_list, name='comment_list'),
    # NEW: Path for listing all comments (if you implement a view for this)
    # NEW URL PATTERN FOR ADDING VESSEL WITH DECKS
    path('add_vessel/', views.add_vessel_with_decks, name='add_vessel_with_decks'),
    # NEW: Path for showing a single comment's details
    path('comments/<int:pk>/', views.comment_detail, name='comment_detail'),
    # NEW: Path for editing a specific comment
    path('comments/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    # NEW: Custom Login and Logout Paths
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
]
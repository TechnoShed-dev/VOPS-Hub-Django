# VOPS-Hub/vops_info_hub/urls.py
from django.contrib import admin
from django.urls import path, include # Add include here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('core_app.urls')), # NEW LINE: Directs /app/ URLs to core_app
]
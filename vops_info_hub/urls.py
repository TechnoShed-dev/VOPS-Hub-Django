# VOPS-Hub/vops_info_hub/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView # NEW IMPORT

urlpatterns = [
    # NEW: Redirect root URL to /app/vessels/
    path('', RedirectView.as_view(url='app/vessels/', permanent=False)),
    path('admin/', admin.site.urls),
    path('app/', include('core_app.urls')),
]
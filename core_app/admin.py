# VOPS-Hub/core_app/admin.py
from django.contrib import admin
from .models import VesselParticulars, VesselDeckHeight, VesselComment

# Register your models here.
admin.site.register(VesselParticulars)
admin.site.register(VesselDeckHeight)
admin.site.register(VesselComment)
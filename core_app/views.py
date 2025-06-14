# VOPS-Hub/core_app/views.py

from django.shortcuts import render, get_object_or_404
from .models import VesselParticulars, VesselDeckHeight, VesselComment

def vessel_list(request):
    vessels = VesselParticulars.objects.all().order_by('vessel_name')
    context = {
        'vessels': vessels
    }
    return render(request, 'core_app/vessel_list.html', context)

def vessel_detail(request, pk):
    vessel = get_object_or_404(VesselParticulars, pk=pk)
    # Sort deck heights by the new 'deck_name' for alphanumeric order
    deck_heights = vessel.vesseldeckheight_set.all().order_by('deck_name') # CHANGED to 'deck_name'
    comments = vessel.vesselcomment_set.all().order_by('-date_of_comment')
    context = {
        'vessel': vessel,
        'deck_heights': deck_heights,
        'comments': comments
    }
    return render(request, 'core_app/vessel_detail.html', context)
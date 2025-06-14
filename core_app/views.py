# VOPS-Hub/core_app/views.py
from django.shortcuts import render, get_object_or_404
from .models import VesselParticulars, VesselDeckHeight, VesselComment

def vessel_list(request):
    """
    Displays a list of all vessels.
    """
    vessels = VesselParticulars.objects.all().order_by('vessel_name')
    context = {
        'vessels': vessels
    }
    return render(request, 'core_app/vessel_list.html', context)

def vessel_detail(request, pk):
    """
    Displays the detailed information for a single vessel,
    including its deck heights and comments.
    """
    vessel = get_object_or_404(VesselParticulars, pk=pk)
    # The related_name 'deck_heights' and 'comments' allow us to access these easily
    deck_heights = vessel.deck_heights.all().order_by('deck_number')
    comments = vessel.comments.all().order_by('-date_of_comment') # Latest comments first

    context = {
        'vessel': vessel,
        'deck_heights': deck_heights,
        'comments': comments,
    }
    return render(request, 'core_app/vessel_detail.html', context)
# VOPS-Hub/core_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # NEW IMPORT

from django.contrib.auth.models import Group # NEW IMPORT - for checking group membership
from django.http import HttpResponseForbidden # NEW IMPORT - for access denied
from django.contrib.auth.forms import AuthenticationForm # NEW IMPORT
from django.contrib.auth import login, logout # NEW IMPORTS
from django.urls import reverse # NEW IMPORT, useful for redirects
from django.conf import settings # NEW IMPORT, to access LOGIN_REDIRECT_URL
from django.db import transaction # For atomic saving of vessel and decks
from django.urls import reverse_lazy # For redirecting after successful save
from .decorators import group_required # Our custom decorator

# Import your new forms
from .forms import VesselParticularsForm, VesselDeckHeightFormSet,VesselCommentForm
# Import your models
from .models import VesselParticulars, VesselComment, VesselDeckHeight

def vessel_list(request):
    vessels = VesselParticulars.objects.all().order_by('vessel_name')
    # NEW: Determine if the user is in the 'Office' group or is a superuser
    user_in_office_group = False
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='Office').exists():
            user_in_office_group = True

    context = {
        'vessels': vessels,
        'user_in_office_group': user_in_office_group, # ADD THIS TO CONTEXT
    }
    return render(request, 'core_app/vessel_list.html', context)

def vessel_detail(request, pk):
    vessel = get_object_or_404(VesselParticulars, pk=pk)
    deck_heights = vessel.vesseldeckheight_set.all().order_by('deck_id')
    comments = vessel.vesselcomment_set.all().order_by('-date_of_comment')

    # NEW: Determine if the user can add/edit comments
    user_can_add_edit_comments = False
    if request.user.is_authenticated:
        if request.user.groups.filter(name='RedVests').exists():
            user_can_add_edit_comments = True

    context = {
        'vessel': vessel,
        'deck_heights': deck_heights,
        'comments': comments,
        'user_can_add_edit_comments': user_can_add_edit_comments, # NEW CONTEXT VARIABLE
    }
    return render(request, 'core_app/vessel_detail.html', context)


@login_required
def add_comment(request, pk):
    vessel = get_object_or_404(VesselParticulars, pk=pk)

    if not request.user.groups.filter(name='RedVests').exists():
        return HttpResponseForbidden("You do not have permission to add comments. Please log in as a RedVest user.")

    if request.method == 'POST':
        form = VesselCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False) # Create comment object but don't save yet
            comment.related_vessel = vessel
            comment.comment_by = request.user # NEW: Set comment_by automatically
            comment.save() # Now save the comment
            return redirect('core_app:vessel_detail', pk=vessel.pk)
    else:
        form = VesselCommentForm()

    context = {
        'form': form,
        'vessel': vessel,
    }
    return render(request, 'core_app/add_comment.html', context)


def comment_list(request):
    # Retrieve all comments, ordered by date_of_comment (most recent first)
    comments = VesselComment.objects.all().order_by('-date_of_comment')
    context = {
        'comments': comments
    }
    return render(request, 'core_app/comment_list.html', context)

# NEW VIEW FOR DISPLAYING SINGLE COMMENT DETAILS
def comment_detail(request, pk):
    comment = get_object_or_404(VesselComment, pk=pk)

    user_can_add_edit_comments = False
    if request.user.is_authenticated:
        if request.user.groups.filter(name='RedVests').exists():
            user_can_add_edit_comments = True

    # NEW: Get 'next' URL parameter from the request
    # Default to the comment list if 'next' is not provided
    next_url = request.GET.get('next', reverse('core_app:comment_list'))

    context = {
        'comment': comment,
        'user_can_add_edit_comments': user_can_add_edit_comments,
        'next_url': next_url, # NEW CONTEXT VARIABLE
    }
    return render(request, 'core_app/comment_detail.html', context)

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(VesselComment, pk=pk)

    if not request.user.groups.filter(name='RedVests').exists():
        return HttpResponseForbidden("You do not have permission to edit comments. Please log in as a RedVest user.")

    if request.method == 'POST':
        # The form will only update 'comment_title' and 'comment_details'
        form = VesselCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save() # Saves the updated title and details
            return redirect('core_app:comment_detail', pk=comment.pk)
    else:
        form = VesselCommentForm(instance=comment) # Pre-populates title and details

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'core_app/edit_comment.html', context)

# NEW: Custom Login View
def custom_login(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL) # Redirect already logged-in users

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) # Logs the user in
            return redirect(settings.LOGIN_REDIRECT_URL) # Redirect to specified URL
    else:
        form = AuthenticationForm() # Empty form for GET request

    context = {'form': form}
    return render(request, 'core_app/login.html', context) # Render custom login template

# NEW: Custom Logout View
@login_required # Only logged-in users can log out
def custom_logout(request):
    logout(request) # Logs the user out
    return redirect(settings.LOGOUT_REDIRECT_URL) # Redirect to specified URL

# NEW VIEW: Add Vessel with Decks
@group_required('Office', redirect_url='core_app:vessel_list') # Only 'Office' group can access
@login_required # Ensure user is logged in
def add_vessel_with_decks(request):
    if request.method == 'POST':
        vessel_form = VesselParticularsForm(request.POST)
        # Pass the request.POST and request.FILES to the formset
        # instance=None because we are creating a new vessel
        deck_formset = VesselDeckHeightFormSet(request.POST, request.FILES, instance=None)

        if vessel_form.is_valid() and deck_formset.is_valid():
            with transaction.atomic(): # Ensures all saves succeed or none are saved
                vessel = vessel_form.save() # Save the vessel first

                # Associate each valid deck form with the new vessel
                for form in deck_formset:
                    if form.cleaned_data: # Only save forms with data
                        # Check if the form is marked for deletion (if editing existing)
                        # For adding new, this mainly checks if it's not an empty form
                        if form.cleaned_data.get('DELETE'):
                            continue # Skip deleted forms

                        deck_height = form.save(commit=False)
                        deck_height.vessel = vessel # Link to the newly created vessel
                        deck_height.save()

            return redirect(reverse_lazy('core_app:vessel_list')) # Redirect to vessel list after success
        else:
            # If forms are not valid, they will be rendered again with errors
            pass
    else: # GET request
        vessel_form = VesselParticularsForm()
        deck_formset = VesselDeckHeightFormSet(instance=None) # Start with empty formset

    context = {
        'vessel_form': vessel_form,
        'deck_formset': deck_formset,
        'title': 'Add New Vessel and Decks' # Title for the template
    }
    return render(request, 'core_app/add_vessel_with_decks.html', context)



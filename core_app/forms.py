# VOPS-Hub/core_app/forms.py
from django import forms
from .models import VesselComment
from django.forms import inlineformset_factory
from .models import VesselParticulars, VesselDeckHeight,VesselComment

class VesselParticularsForm(forms.ModelForm):
    class Meta:
        model = VesselParticulars
        fields = [
            'vessel_name', 'capacity', 'number_of_decks',
            'general_notes', 'additional_hazards', 'deck_layout_link',
            'risk_assessment_document_link', 'vessel_info_link'
        ]
        widgets = {
            'general_notes': forms.Textarea(attrs={'rows': 3}),
            'additional_hazards': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'vessel_name': 'Vessel Name',
            'capacity': 'Capacity',
            'number_of_decks': 'Number of Decks',
            'general_notes': 'General Notes',
            'additional_hazards': 'Additional Hazards',
            'deck_layout_link': 'Deck Layout Link',
            'risk_assessment_document_link': 'Risk Assessment Document Link',
            'vessel_info_link': 'Vessel Info Link',
        }

class VesselDeckHeightForm(forms.ModelForm):
    class Meta:
        model = VesselDeckHeight
        # 'vessel' field is excluded because it will be set by the formset
        fields = ['deck_id', 'deck_name', 'average_deck_height_m', 'deck_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'deck_id': 'Deck ID',
            'deck_name': 'Deck Name',
            'average_deck_height_m': 'Avg. Height (m)',
            'deck_type': 'Deck Type',
            'notes': 'Notes',
        }

# Inline formset for VesselDeckHeight related to VesselParticulars
# extra=1: Start with one empty form for a new deck height
# can_delete=True: Allow deleting existing deck heights (if editing)
# max_num=10: Limit to a maximum of 10 deck height forms
VesselDeckHeightFormSet = inlineformset_factory(
    VesselParticulars,
    VesselDeckHeight,
    form=VesselDeckHeightForm,
    extra=1,
    can_delete=True,
    max_num=16, # You can adjust this limit
)
class VesselCommentForm(forms.ModelForm):
    class Meta:
        model = VesselComment
        fields = ['comment_title', 'comment_details']
        widgets = {
            'comment_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter comment title'}),
            'comment_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter detailed comment here...'}),
        }
        labels = {
            'comment_title': 'Title',
            'comment_details': 'Details',
        }
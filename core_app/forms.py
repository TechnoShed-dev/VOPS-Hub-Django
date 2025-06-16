# VOPS-Hub/core_app/forms.py
from django import forms
from .models import VesselComment

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
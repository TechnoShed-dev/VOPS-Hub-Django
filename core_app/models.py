# VOPS-Hub/core_app/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings # NEW IMPORT: To reference AUTH_USER_MODEL

class VesselParticulars(models.Model):
    vessel_name = models.CharField(max_length=255, unique=True)
    capacity = models.FloatField(null=True, blank=True)
    number_of_decks = models.IntegerField(null=True, blank=True)
    general_notes = models.TextField(blank=True, null=True)
    additional_hazards = models.TextField(blank=True, null=True)
    deck_layout_link = models.URLField(max_length=500, blank=True, null=True)
    risk_assessment_document_link = models.URLField(max_length=500, blank=True, null=True)
    vessel_info_link = models.URLField(max_length=500, blank=True, null=True) # NEW FIELD

    def __str__(self):
        return self.vessel_name

class VesselDeckHeight(models.Model):
    vessel = models.ForeignKey(VesselParticulars, on_delete=models.CASCADE)
    deck_id = models.IntegerField(null=True, blank=True) # NEW: Integer ID for deck
    deck_name = models.CharField(max_length=100, blank=True, null=True) # NEW: Alphanumeric name for deck
    average_deck_height_m = models.FloatField(null=True, blank=True)
    deck_type = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('vessel', 'deck_id') # Ensure unique deck ID per vessel
        ordering = ['deck_id'] # Default ordering, can be overridden in views

    def __str__(self):
        return f"{self.vessel.vessel_name} - Deck {self.deck_name} (ID: {self.deck_id})"

class VesselComment(models.Model):
    comment_title = models.CharField(max_length=255)
    comment_details = models.TextField()
    date_of_comment = models.DateTimeField(default=timezone.now)
    # Ensure this line is correct:
    comment_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='vessel_comments')
    related_vessel = models.ForeignKey(VesselParticulars, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date_of_comment'] # Newest comments first

    def __str__(self):
        return f"Comment by {self.comment_by.username if self.comment_by else 'Anonymous'} on {self.related_vessel.vessel_name if self.related_vessel else 'N/A'}"
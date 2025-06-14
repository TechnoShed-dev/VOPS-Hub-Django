# VOPS-Hub/core_app/models.py
from django.db import models

class VesselParticulars(models.Model):
    """
    Represents the basic details of a vessel.
    Reflects the latest 'Vessel Details' sheet columns, with Capacity as Integer.
    """
    vessel_name = models.CharField(max_length=255, unique=True, verbose_name="Vessel Name")
    capacity = models.IntegerField(null=True, blank=True, verbose_name="Capacity") # CHANGED TO INTEGERFIELD
    number_of_decks = models.IntegerField(null=True, blank=True, verbose_name="Number of Decks")
    general_notes = models.TextField(null=True, blank=True, verbose_name="General Notes")
    additional_hazards = models.TextField(null=True, blank=True, verbose_name="Additional Hazards")
    deck_layout_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="Deck Layout Link")
    risk_assessment_document_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="Risk Assessment Document Link")

    class Meta:
        verbose_name = "Vessel Detail"
        verbose_name_plural = "Vessel Details"
        ordering = ['vessel_name'] # Default ordering for lists

    def __str__(self):
        return self.vessel_name

class VesselDeckHeight(models.Model):
    """
    Represents the deck heights for a specific vessel.
    Reflects the latest 'Deck Heights' sheet columns.
    """
    # Foreign Key to VesselParticulars
    vessel = models.ForeignKey(
        VesselParticulars,
        on_delete=models.CASCADE,
        related_name='deck_heights',
        verbose_name="Vessel"
    )
    deck_number = models.CharField(max_length=50, verbose_name="Deck Number")
    average_deck_height_m = models.FloatField(null=True, blank=True, verbose_name="Average Deck Height (m)")
    deck_type = models.CharField(max_length=255, null=True, blank=True, verbose_name="Deck Type")
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('vessel', 'deck_number'),)
        verbose_name = "Vessel Deck Height"
        verbose_name_plural = "Vessel Deck Heights"
        ordering = ['vessel', 'deck_number']

    def __str__(self):
        return f"{self.vessel.vessel_name} - Deck {self.deck_number} ({self.average_deck_height_m}m)"

class VesselComment(models.Model):
    """
    Represents comments related to a vessel.
    Reflects the 'Comments' sheet columns (unchanged).
    """
    comment_title = models.CharField(max_length=255, verbose_name="Comment Title")
    comment_details = models.TextField(verbose_name="Comment Details")
    date_of_comment = models.DateTimeField(verbose_name="Date of Comment")
    comment_by = models.CharField(max_length=255, null=True, blank=True, verbose_name="Comment By")
    related_vessel = models.ForeignKey(
        VesselParticulars,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='comments',
        verbose_name="Related Vessel"
    )

    class Meta:
        verbose_name = "Vessel Comment"
        verbose_name_plural = "Vessel Comments"
        ordering = ['-date_of_comment']

    def __str__(self):
        if self.related_vessel:
            return f"Comment on {self.related_vessel.vessel_name}: {self.comment_title}"
        else:
            return f"General Comment: {self.comment_title}"
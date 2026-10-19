from django.db import models
from django.conf import settings
from apps.listings.models import Listing

class Offer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Seller Review'),
        ('countered_by_seller', 'Countered by Seller'),
        ('countered_by_buyer', 'Countered by Buyer'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed & Settled'),
    )

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='offers')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers_made')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers_received')
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    last_actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='last_negotiation_moves')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['listing', 'status']),
        ]

    def __str__(self):
        return f"Offer #{self.id} on '{self.listing.title}': ${self.current_amount} [{self.status}]"

class OfferHistory(models.Model):
    ACTION_CHOICES = (
        ('initial_offer', 'Initial Offer'),
        ('counter_offer', 'Counter Offer'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    )

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='history')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=25, choices=ACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.actor.username} {self.action} ${self.amount} at {self.timestamp}"

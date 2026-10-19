from django.db import models
from django.conf import settings
from apps.listings.models import Listing
from apps.offers.models import Offer

class Review(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['offer', 'reviewer'], name='unique_offer_reviewer'),
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='check_valid_rating_range'
            )
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Update reviewee user average rating
            reviews = Review.objects.filter(reviewee=self.reviewee)
            total = sum(r.rating for r in reviews)
            count = reviews.count()
            if count > 0:
                self.reviewee.rating_avg = round(total / count, 2)
                self.reviewee.rating_count = count
                self.reviewee.save(update_fields=['rating_avg', 'rating_count'])

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}: {self.rating}★"

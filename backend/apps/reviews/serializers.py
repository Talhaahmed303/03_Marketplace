from rest_framework import serializers
from .models import Review
from apps.users.serializers import UserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    reviewee = UserSerializer(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'listing', 'listing_title', 'offer', 'reviewer', 'reviewee', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'reviewer', 'reviewee', 'listing', 'created_at')

class CreateReviewSerializer(serializers.Serializer):
    offer_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(min_length=3)

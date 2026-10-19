from rest_framework import serializers
from .models import Offer, OfferHistory
from apps.listings.models import Listing
from apps.users.serializers import UserSerializer

class OfferHistorySerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    actor_role = serializers.CharField(source='actor.role', read_only=True)

    class Meta:
        model = OfferHistory
        fields = ('id', 'actor', 'actor_username', 'actor_role', 'action', 'amount', 'message', 'timestamp')
        read_only_fields = ('id', 'actor', 'timestamp')

class OfferListingSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ('id', 'title', 'slug', 'price', 'status', 'image_url')

class OfferSerializer(serializers.ModelSerializer):
    listing = OfferListingSummarySerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    last_actor_username = serializers.CharField(source='last_actor.username', read_only=True)
    history = OfferHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = (
            'id', 'listing', 'buyer', 'seller', 'initial_amount', 'current_amount',
            'status', 'last_actor', 'last_actor_username', 'history', 'created_at', 'updated_at'
        )
        read_only_fields = fields

class CreateOfferSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    message = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Offer amount must be greater than zero.")
        return value

class CounterOfferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    message = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Counter offer amount must be greater than zero.")
        return value

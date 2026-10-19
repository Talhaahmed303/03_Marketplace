from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Review
from apps.offers.models import Offer
from .serializers import ReviewSerializer, CreateReviewSerializer

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Review.objects.select_related('reviewer', 'reviewee', 'listing', 'offer').all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(reviewee_id=user_id)
        listing_id = self.request.query_params.get('listing_id')
        if listing_id:
            qs = qs.filter(listing_id=listing_id)
        return qs

    def post(self, request, *args, **kwargs):
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer_id = serializer.validated_data['offer_id']
        rating = serializer.validated_data['rating']
        comment = serializer.validated_data['comment']

        offer = get_object_or_404(Offer, id=offer_id)

        # Eligibility Gate 1: Offer must be strictly in completed status
        if offer.status != 'completed':
            return Response(
                {'detail': f'Cannot review transaction. Only completed transactions can be reviewed (current status: {offer.status}).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Eligibility Gate 2: Request user must be a legitimate participant
        if request.user != offer.buyer and request.user != offer.seller:
            return Response(
                {'detail': 'You are not a participant in this completed transaction and cannot leave a review.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Eligibility Gate 3: Single review per participant constraint
        if Review.objects.filter(offer=offer, reviewer=request.user).exists():
            return Response(
                {'detail': 'You have already submitted a review for this transaction.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reviewee = offer.seller if request.user == offer.buyer else offer.buyer

        review = Review.objects.create(
            listing=offer.listing,
            offer=offer,
            reviewer=request.user,
            reviewee=reviewee,
            rating=rating,
            comment=comment
        )

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

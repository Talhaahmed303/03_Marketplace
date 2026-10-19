from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Offer, OfferHistory
from apps.listings.models import Listing
from .serializers import (
    OfferSerializer,
    CreateOfferSerializer,
    CounterOfferSerializer
)

class OfferListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OfferSerializer

    def get_queryset(self):
        user = self.request.user
        role_filter = self.request.query_params.get('as')
        if role_filter == 'buyer':
            return Offer.objects.filter(buyer=user).select_related('listing', 'buyer', 'seller', 'last_actor').prefetch_related('history__actor')
        elif role_filter == 'seller':
            return Offer.objects.filter(seller=user).select_related('listing', 'buyer', 'seller', 'last_actor').prefetch_related('history__actor')
        return Offer.objects.filter(buyer=user) | Offer.objects.filter(seller=user)

    def post(self, request, *args, **kwargs):
        serializer = CreateOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing_id = serializer.validated_data['listing_id']
        amount = serializer.validated_data['amount']
        message = serializer.validated_data.get('message', '')

        listing = get_object_or_404(Listing, id=listing_id)

        # Validation: Cannot make offer on your own listing
        if listing.seller == request.user:
            return Response(
                {'detail': 'You cannot make an offer on your own listing.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation: Listing must be active
        if listing.status != 'active':
            return Response(
                {'detail': f'This listing is currently {listing.status} and cannot receive new offers.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            offer = Offer.objects.create(
                listing=listing,
                buyer=request.user,
                seller=listing.seller,
                initial_amount=amount,
                current_amount=amount,
                status='pending',
                last_actor=request.user
            )

            OfferHistory.objects.create(
                offer=offer,
                actor=request.user,
                action='initial_offer',
                amount=amount,
                message=message or f"Offered ${amount}"
            )

        return Response(OfferSerializer(offer).data, status=status.HTTP_201_CREATED)

class OfferDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OfferSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Offer.objects.all().select_related('listing', 'buyer', 'seller', 'last_actor').prefetch_related('history__actor')
        return Offer.objects.filter(buyer=user) | Offer.objects.filter(seller=user)

class CounterOfferView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CounterOfferSerializer

    def post(self, request, pk):
        offer = get_object_or_404(Offer, id=pk)
        user = request.user

        # Permission: Only buyer or seller
        if offer.buyer != user and offer.seller != user and not (user.is_staff or user.role == 'admin'):
            return Response({'detail': 'You are not a party to this negotiation.'}, status=status.HTTP_403_FORBIDDEN)

        # State check: Cannot counter terminal offers
        if offer.status in ['accepted', 'declined', 'completed']:
            return Response({'detail': f'Cannot counter an offer that is already {offer.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        # Turn check: Cannot counter your own move
        if offer.last_actor == user:
            return Response({'detail': 'Awaiting response from counter-party. You cannot counter your own move.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CounterOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        message = serializer.validated_data.get('message', '')

        with transaction.atomic():
            new_status = 'countered_by_seller' if user == offer.seller else 'countered_by_buyer'
            offer.current_amount = amount
            offer.status = new_status
            offer.last_actor = user
            offer.save()

            OfferHistory.objects.create(
                offer=offer,
                actor=user,
                action='counter_offer',
                amount=amount,
                message=message or f"Countered with ${amount}"
            )

        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)

class AcceptOfferView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OfferSerializer

    def post(self, request, pk):
        offer = get_object_or_404(Offer, id=pk)
        user = request.user

        if offer.buyer != user and offer.seller != user and not (user.is_staff or user.role == 'admin'):
            return Response({'detail': 'You are not a party to this negotiation.'}, status=status.HTTP_403_FORBIDDEN)

        if offer.status in ['accepted', 'declined', 'completed']:
            return Response({'detail': f'Cannot accept an offer that is already {offer.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        # Turn check: Cannot accept your own offer
        if offer.last_actor == user and not (user.is_staff or user.role == 'admin'):
            return Response({'detail': 'You cannot accept your own counter-offer. Await counter-party acceptance.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            offer.status = 'accepted'
            offer.save()

            # Reserve listing
            offer.listing.status = 'reserved'
            offer.listing.save()

            OfferHistory.objects.create(
                offer=offer,
                actor=user,
                action='accepted',
                amount=offer.current_amount,
                message=f"Accepted offer of ${offer.current_amount}"
            )

        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)

class DeclineOfferView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OfferSerializer

    def post(self, request, pk):
        offer = get_object_or_404(Offer, id=pk)
        user = request.user

        if offer.buyer != user and offer.seller != user and not (user.is_staff or user.role == 'admin'):
            return Response({'detail': 'You are not a party to this negotiation.'}, status=status.HTTP_403_FORBIDDEN)

        if offer.status in ['accepted', 'declined', 'completed']:
            return Response({'detail': f'Offer is already {offer.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            offer.status = 'declined'
            offer.save()

            OfferHistory.objects.create(
                offer=offer,
                actor=user,
                action='declined',
                amount=offer.current_amount,
                message="Declined negotiation"
            )

        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)

class CompleteOfferView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OfferSerializer

    def post(self, request, pk):
        offer = get_object_or_404(Offer, id=pk)
        user = request.user

        if offer.buyer != user and offer.seller != user and not (user.is_staff or user.role == 'admin'):
            return Response({'detail': 'You are not authorized to complete this transaction.'}, status=status.HTTP_403_FORBIDDEN)

        if offer.status != 'accepted':
            return Response({'detail': f'Cannot complete an offer with status "{offer.status}". Must be "accepted" first.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            offer.status = 'completed'
            offer.save()

            offer.listing.status = 'sold'
            offer.listing.save()

            OfferHistory.objects.create(
                offer=offer,
                actor=user,
                action='completed',
                amount=offer.current_amount,
                message="Transaction finalized and completed successfully."
            )

        return Response(OfferSerializer(offer).data, status=status.HTTP_200_OK)

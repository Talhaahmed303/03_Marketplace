from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Listing
from .serializers import CategorySerializer, ListingSerializer
from .permissions import IsSellerOrReadOnly

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)

class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = (IsSellerOrReadOnly,)

    def get_queryset(self):
        qs = Listing.objects.select_related('seller', 'category').all()
        # Filter by category
        category_param = self.request.query_params.get('category')
        if category_param:
            qs = qs.filter(category__slug=category_param)

        # Filter by status (default active for unauthenticated or general feed, unless specified)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        elif not self.request.user.is_authenticated or self.action == 'list':
            # By default in list view, show active listings unless user filters by my_listings
            if self.request.query_params.get('my') == 'true' and self.request.user.is_authenticated:
                qs = qs.filter(seller=self.request.user)
            else:
                qs = qs.filter(status='active')

        # Keyword Search
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        # Price range filter
        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                qs = qs.filter(price__gte=float(min_price))
            except ValueError:
                pass
        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                qs = qs.filter(price__lte=float(max_price))
            except ValueError:
                pass

        return qs

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

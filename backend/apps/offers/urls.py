from django.urls import path
from .views import (
    OfferListCreateView,
    OfferDetailView,
    CounterOfferView,
    AcceptOfferView,
    DeclineOfferView,
    CompleteOfferView
)

urlpatterns = [
    path('', OfferListCreateView.as_view(), name='offer-list-create'),
    path('<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('<int:pk>/counter/', CounterOfferView.as_view(), name='offer-counter'),
    path('<int:pk>/accept/', AcceptOfferView.as_view(), name='offer-accept'),
    path('<int:pk>/decline/', DeclineOfferView.as_view(), name='offer-decline'),
    path('<int:pk>/complete/', CompleteOfferView.as_view(), name='offer-complete'),
]

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Domain APIs
    path('api/auth/', include('apps.users.urls')),
    path('api/listings/', include('apps.listings.urls')),
    path('api/offers/', include('apps.offers.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
]

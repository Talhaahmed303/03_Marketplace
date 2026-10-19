from django.urls import path
from .views import RegisterView, CustomLoginView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', CustomLoginView.as_view(), name='auth-login'),
    path('profile/', UserProfileView.as_view(), name='auth-profile'),
]

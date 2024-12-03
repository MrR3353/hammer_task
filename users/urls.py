from django.urls import path
from .views import SendAuthCodeView, VerifyAuthCodeView, ProfileView

urlpatterns = [
    path('auth/send-code/', SendAuthCodeView.as_view(), name='send_auth_code'),
    path('auth/verify-code/', VerifyAuthCodeView.as_view(), name='verify_auth_code'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
]
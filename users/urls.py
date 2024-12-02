from django.urls import path
from .views import SendAuthCodeView, VerifyAuthCodeView

urlpatterns = [
    path('auth/send-code/', SendAuthCodeView.as_view(), name='send_auth_code'),
    path('auth/verify-code/', VerifyAuthCodeView.as_view(), name='verify_auth_code'),
]
from django.urls import path
from .views import SendAuthCodeView, VerifyAuthCodeView, ProfileView, ActivateInviteView

urlpatterns = [
    path('send-code/', SendAuthCodeView.as_view(), name='send_auth_code'),
    path('verify-code/', VerifyAuthCodeView.as_view(), name='verify_auth_code'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('activate-invite/', ActivateInviteView.as_view(), name='activate-invite'),
]
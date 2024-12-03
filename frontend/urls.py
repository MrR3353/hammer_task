from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # path('send-code/', SendAuthCodeView.as_view(), name='send_auth_code'),
    # path('verify-code/', VerifyAuthCodeView.as_view(), name='verify_auth_code'),
    # path('profile/', ProfileView.as_view(), name='profile'),
    # path('activate-invite/', ActivateInviteView.as_view(), name='activate-invite'),
    path('send-code/', TemplateView.as_view(template_name="send_code.html"), name="send_code_template"),
    path('verify-code/', TemplateView.as_view(template_name="verify_code.html"), name="verify_code_template"),
    path('profile/', TemplateView.as_view(template_name="profile.html"), name="profile_template"),
]
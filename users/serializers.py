from rest_framework import serializers

from .models import User


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        help_text="Введите номер телефона для отправки кода авторизации"
    )


class VerificationCodeSerializer(PhoneNumberSerializer):
    code = serializers.IntegerField(min_value=1000, max_value=9999)


class TokenWithPhoneSerializer(PhoneNumberSerializer):
    token = serializers.CharField(max_length=40)


class ProfileSerializer(serializers.ModelSerializer):
    referrals_phones = serializers.ListSerializer(child=PhoneNumberSerializer())

    class Meta:
        model = User
        fields = ['phone_number', 'invite_code', 'activated_invite_code', 'referrals_phones']


class ActivateInviteSerializer(serializers.Serializer):
    invite_code = serializers.CharField(min_length=6, max_length=6)
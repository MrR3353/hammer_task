from typing import List

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
    referrals = serializers.ListSerializer(child=PhoneNumberSerializer())

    class Meta:
        model = User
        fields = ['phone_number', 'invite_code', 'activated_invite_code', 'referrals']


class ActivateInviteSerializer(serializers.Serializer):
    activated_invite_code = serializers.CharField(min_length=6, max_length=6)

    def validate_activated_invite_code(self, code: str) -> str:
        if not User.objects.filter(activated_invite_code=code).exists():
            raise serializers.ValidationError('Такого инвайт кода не существует.')
        return code

    def update(self, instance, validated_data):
        if instance.activated_invite_code:
            raise serializers.ValidationError('Инвайт код уже был активирован.')
        instance.activated_invite_code = validated_data['activated_invite_code']
        instance.save()
        return instance

# class UserCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['phone_number']
#
#     def validate_phone_number(self, phone: str) -> str:
#         if User.objects.filter(phone_number=phone).exists():
#             raise serializers.ValidationError('Пользователь с таким номером телефона уже существует.')
#         return phone
#
#     def create(self, validated_data: dict):
#         return User.objects.create(**validated_data)

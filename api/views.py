import random
import time

from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, AuthCode
from .serializers import PhoneNumberSerializer, VerificationCodeSerializer, TokenWithPhoneSerializer, ProfileSerializer, \
    ActivateInviteSerializer


class SendAuthCodeView(APIView):
    @extend_schema(
        summary="Отправка кода авторизации",
        description="Отправляет 4-значный код.",
        request=PhoneNumberSerializer,
        responses={
            200: VerificationCodeSerializer
        }
    )
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = random.randint(1000, 9999)
            AuthCode.objects.update_or_create(
                phone_number=phone_number,
                defaults={"code": code, "created_at": now()}
            )
            # имитация задержки при отправке кода
            time.sleep(1)
            return Response({'phone_number': phone_number, 'code': code}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyAuthCodeView(APIView):
    @extend_schema(
        summary="Проверка кода авторизации",
        description="Проверяет валидность кода и выполняет авторизацию, возращает access токен",
        request=VerificationCodeSerializer,
        responses={
            200: TokenWithPhoneSerializer
        }
    )
    def post(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']

            try:
                auth_code = AuthCode.objects.get(phone_number=phone_number)
            except AuthCode.DoesNotExist:
                return Response({"error": "Неверный код или номер телефона"}, status=status.HTTP_404_NOT_FOUND)

            if auth_code.code != code:
                return Response({"error": "Код неверный"}, status=status.HTTP_400_BAD_REQUEST)

            if auth_code.is_expired():
                AuthCode.objects.get(phone_number=phone_number).delete()
                return Response({"error": "Срок действия кода истек"}, status=status.HTTP_400_BAD_REQUEST)

            AuthCode.objects.get(phone_number=phone_number).delete()
            user, created = User.objects.get_or_create(phone_number=phone_number)
            print(user, type(user))
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "phone_number": user.phone_number,
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Получение профиля пользователя",
        description="Получает профиль пользователя, используя access токен",
        responses={
            200: ProfileSerializer
        }
    )
    def get(self, request):
        user = request.user
        referrals_phones = User.objects.filter(activated_invite_code=user.invite_code).values_list('phone_number', flat=True)
        return Response({
            "phone_number": user.phone_number,
            "invite_code": user.invite_code,
            "activated_invite_code": user.activated_invite_code,
            "referrals_phones": referrals_phones,
        }, status=status.HTTP_200_OK)


class ActivateInviteView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Активация инвайт кода",
        description="Активирует инвайт код другого пользователя, если он существует",
        request=ActivateInviteSerializer
    )
    def post(self, request):
        serializer = ActivateInviteSerializer(data=request.data)
        user = request.user
        if user.activated_invite_code:
            return Response({"error": "Инвайт код уже был активирован"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            invite_code = serializer.validated_data['invite_code']
            try:
                invite_owner = User.objects.get(invite_code=invite_code)
            except User.DoesNotExist:
                return Response({"error": "Несуществующий инвайт код"}, status=status.HTTP_404_NOT_FOUND)

            if user == invite_owner:
                return Response({"error": "Нельзя активировать собственный инвайт код"}, status=status.HTTP_400_BAD_REQUEST)

            user.activated_invite_code = invite_code
            user.save()
            return Response({}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
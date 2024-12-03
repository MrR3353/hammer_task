import random
import time

from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, AuthCode
from .serializers import PhoneNumberSerializer, VerificationCodeSerializer


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
        description="Проверяет валидность кода и выполняет авторизацию",
        request=VerificationCodeSerializer,
        responses={
            200: VerificationCodeSerializer
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

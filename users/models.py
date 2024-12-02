import datetime

import shortuuid
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now


class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6, unique=True)
    activated_invite_code = models.CharField(max_length=6, blank=True, null=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            while True:
                code = User.generate_invite_code()
                if not User.objects.filter(invite_code=code).exists():
                    self.invite_code = code
                    break
        super().save(*args, **kwargs)

    @staticmethod
    def generate_invite_code() -> str:
        return shortuuid.ShortUUID().random(length=6)


class AuthCode(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    code = models.IntegerField(validators=[MinValueValidator(9999), MaxValueValidator(9999)])
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        expiration_time = self.created_at + datetime.timedelta(minutes=2)
        return now() > expiration_time
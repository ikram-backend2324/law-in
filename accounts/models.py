from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_ABITURIYENT = 'abituriyent'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_ABITURIYENT, 'Abituriyent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ABITURIYENT)
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser or self.is_staff

    def is_abituriyent(self):
        return self.role == self.ROLE_ABITURIYENT

    def __str__(self):
        return self.full_name or self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

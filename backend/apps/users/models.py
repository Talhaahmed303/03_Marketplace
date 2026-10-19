from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=150, blank=True, default='')
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    rating_count = models.PositiveIntegerField(default=0)

    def is_seller(self):
        return self.role == 'seller' or self.is_staff or self.role == 'admin'

    def is_administrator(self):
        return self.role == 'admin' or self.is_staff

    def __str__(self):
        return f"{self.username} ({self.role})"

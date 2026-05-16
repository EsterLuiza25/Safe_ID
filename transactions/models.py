import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Transaction(models.Model):
    class Status(models.TextChoices):
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    customer_id = models.CharField(max_length=64)
    ip_address = models.GenericIPAddressField()
    device_fingerprint = models.CharField(max_length=255)
    risk_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        default=Status.APPROVED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer_id"]),
            models.Index(fields=["device_fingerprint"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.id} - {self.customer_id} - {self.status}"


class DeviceBlacklist(models.Model):
    fingerprint = models.CharField(max_length=255, unique=True)
    reason = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fingerprint"]
        indexes = [
            models.Index(fields=["fingerprint"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        self.fingerprint = self.fingerprint.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.fingerprint} ({status})"

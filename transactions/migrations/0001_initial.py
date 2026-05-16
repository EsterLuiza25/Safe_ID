import uuid

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("customer_id", models.CharField(max_length=64)),
                ("ip_address", models.GenericIPAddressField()),
                ("device_fingerprint", models.CharField(max_length=255)),
                (
                    "risk_score",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                        ],
                        default="APPROVED",
                        max_length=8,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["customer_id"], name="transactio_customer_33f0ad_idx"),
                    models.Index(
                        fields=["device_fingerprint"],
                        name="transactio_device__00f8c7_idx",
                    ),
                    models.Index(fields=["status"], name="transactio_status_f2a852_idx"),
                ],
            },
        ),
    ]

from django.db import migrations, models


def seed_blacklist(apps, schema_editor):
    DeviceBlacklist = apps.get_model("transactions", "DeviceBlacklist")
    fingerprints = [
        ("blacklisted-device-001", "Seed demo fingerprint"),
        ("fraud-emulator-999", "Seed demo fingerprint"),
        ("blocked-fingerprint-demo", "Seed demo fingerprint"),
    ]

    for fingerprint, reason in fingerprints:
        DeviceBlacklist.objects.get_or_create(
            fingerprint=fingerprint,
            defaults={
                "reason": reason,
                "is_active": True,
            },
        )


def unseed_blacklist(apps, schema_editor):
    DeviceBlacklist = apps.get_model("transactions", "DeviceBlacklist")
    DeviceBlacklist.objects.filter(
        fingerprint__in=[
            "blacklisted-device-001",
            "fraud-emulator-999",
            "blocked-fingerprint-demo",
        ],
        reason="Seed demo fingerprint",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0002_rename_transactio_customer_33f0ad_idx_transaction_custome_a08692_idx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceBlacklist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fingerprint", models.CharField(max_length=255, unique=True)),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["fingerprint"],
                "indexes": [
                    models.Index(fields=["fingerprint"], name="transaction_fingerp_fb92b0_idx"),
                    models.Index(fields=["is_active"], name="transaction_is_acti_c006d6_idx"),
                ],
            },
        ),
        migrations.RunPython(seed_blacklist, unseed_blacklist),
    ]

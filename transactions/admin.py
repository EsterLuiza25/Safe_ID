from django.contrib import admin

from .models import DeviceBlacklist, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_id",
        "amount",
        "ip_address",
        "risk_score",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("id", "customer_id", "device_fingerprint", "ip_address")
    readonly_fields = ("id", "created_at")


@admin.register(DeviceBlacklist)
class DeviceBlacklistAdmin(admin.ModelAdmin):
    list_display = ("fingerprint", "is_active", "reason", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("fingerprint", "reason")
    readonly_fields = ("created_at", "updated_at")

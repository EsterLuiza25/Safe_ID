from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.throttles import IPRateThrottle

from .models import DeviceBlacklist, Transaction
from .services.risk_engine import RiskDecision


class AuthorizeTransactionAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("authorize-transaction")
        self.client.credentials(HTTP_X_API_KEY="dev-safeguard-key")

    def test_approved_low_risk_transaction(self):
        payload = {
            "amount": "250.00",
            "customer_id": "customer-123",
            "device_fingerprint": "ios-device-abc",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Transaction.Status.APPROVED)
        self.assertEqual(response.data["risk_score"], 10)
        self.assertEqual(response.data["risk_reasons"], ["LOW_RISK"])
        self.assertEqual(Transaction.objects.count(), 1)

    def test_rejected_transaction_when_amount_is_above_limit(self):
        payload = {
            "amount": "10000.01",
            "customer_id": "customer-456",
            "device_fingerprint": "trusted-device-abc",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Transaction.Status.REJECTED)
        self.assertEqual(response.data["risk_score"], 90)
        self.assertEqual(response.data["risk_reasons"], ["AMOUNT_ABOVE_LIMIT"])

    def test_rejected_transaction_when_device_fingerprint_is_blacklisted(self):
        payload = {
            "amount": "500.00",
            "customer_id": "customer-789",
            "device_fingerprint": "blocked-fingerprint-demo",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Transaction.Status.REJECTED)
        self.assertEqual(response.data["risk_score"], 100)
        self.assertEqual(response.data["risk_reasons"], ["BLACKLISTED_DEVICE"])

    @patch("transactions.views.RiskEngine.evaluate")
    def test_captures_ip_and_user_agent_from_request(self, mock_evaluate):
        mock_evaluate.return_value = RiskDecision(
            status=Transaction.Status.APPROVED,
            risk_score=10,
            reasons=["LOW_RISK"],
        )
        payload = {
            "amount": "100.00",
            "customer_id": "customer-ip-user-agent",
            "device_fingerprint": "web-device-abc",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
            REMOTE_ADDR="10.0.0.10",
            HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.10",
            HTTP_USER_AGENT="SafeGuard-Test-Agent/1.0",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["ip_address"], "203.0.113.10")

        transaction = Transaction.objects.get(id=response.data["id"])
        self.assertEqual(transaction.ip_address, "203.0.113.10")

        mock_evaluate.assert_called_once_with(
            amount=Decimal("100.00"),
            device_fingerprint="web-device-abc",
            ip_address="203.0.113.10",
            user_agent="SafeGuard-Test-Agent/1.0",
        )

    def test_returns_400_when_payload_has_empty_fields(self):
        payload = {
            "amount": "100.00",
            "customer_id": "",
            "device_fingerprint": "",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("customer_id", response.data["details"])
        self.assertIn("device_fingerprint", response.data["details"])
        self.assertEqual(Transaction.objects.count(), 0)

    def test_returns_400_when_amount_is_negative(self):
        payload = {
            "amount": "-1.00",
            "customer_id": "customer-negative",
            "device_fingerprint": "ios-device-abc",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("amount", response.data["details"])
        self.assertEqual(Transaction.objects.count(), 0)

    def test_returns_403_without_api_key(self):
        self.client.credentials()
        payload = {
            "amount": "250.00",
            "customer_id": "customer-123",
            "device_fingerprint": "ios-device-abc",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "permission_denied")
        self.assertEqual(Transaction.objects.count(), 0)


class TransactionQueryAPITests(APITestCase):
    def setUp(self):
        self.client.credentials(HTTP_X_API_KEY="dev-safeguard-key")
        self.list_url = reverse("transaction-list")
        self.approved_transaction = Transaction.objects.create(
            amount=Decimal("250.00"),
            customer_id="customer-approved-123",
            ip_address="127.0.0.1",
            device_fingerprint="trusted-device",
            risk_score=10,
            status=Transaction.Status.APPROVED,
        )
        self.rejected_transaction = Transaction.objects.create(
            amount=Decimal("15000.00"),
            customer_id="customer-rejected-456",
            ip_address="203.0.113.10",
            device_fingerprint="blocked-fingerprint-demo",
            risk_score=100,
            status=Transaction.Status.REJECTED,
        )

    def test_lists_transactions_with_pagination(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filters_transactions_by_status(self):
        response = self.client.get(self.list_url, {"status": Transaction.Status.REJECTED})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], Transaction.Status.REJECTED)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.rejected_transaction.id),
        )

    def test_searches_transactions_by_customer_id(self):
        response = self.client.get(self.list_url, {"customer_id": "approved"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["customer_id"],
            self.approved_transaction.customer_id,
        )

    def test_retrieves_transaction_detail_by_uuid(self):
        detail_url = reverse("transaction-detail", kwargs={"id": self.approved_transaction.id})

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.approved_transaction.id))
        self.assertEqual(response.data["amount"], "250.00")
        self.assertEqual(response.data["customer_id"], "customer-approved-123")
        self.assertEqual(response.data["ip_address"], "127.0.0.1")
        self.assertEqual(response.data["device_fingerprint"], "trusted-device")
        self.assertEqual(response.data["risk_score"], 10)
        self.assertEqual(response.data["status"], Transaction.Status.APPROVED)
        self.assertIn("created_at", response.data)
        self.assertNotIn("risk_reasons", response.data)

    def test_returns_404_when_transaction_does_not_exist(self):
        detail_url = reverse("transaction-detail", kwargs={"id": uuid4()})

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["code"], "not_found")


class DeviceBlacklistTests(APITestCase):
    def setUp(self):
        self.client.credentials(HTTP_X_API_KEY="dev-safeguard-key")
        self.url = reverse("authorize-transaction")

    def test_rejects_transaction_with_active_blacklist_record(self):
        DeviceBlacklist.objects.create(
            fingerprint="persisted-risk-device",
            reason="Teste automatizado",
            is_active=True,
        )
        payload = {
            "amount": "500.00",
            "customer_id": "customer-blacklist",
            "device_fingerprint": "persisted-risk-device",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Transaction.Status.REJECTED)
        self.assertEqual(response.data["risk_reasons"], ["BLACKLISTED_DEVICE"])

    def test_ignores_inactive_blacklist_record(self):
        DeviceBlacklist.objects.create(
            fingerprint="inactive-risk-device",
            reason="Teste automatizado",
            is_active=False,
        )
        payload = {
            "amount": "500.00",
            "customer_id": "customer-inactive-blacklist",
            "device_fingerprint": "inactive-risk-device",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Transaction.Status.APPROVED)
        self.assertEqual(response.data["risk_reasons"], ["LOW_RISK"])


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "rate-limit-tests",
        }
    },
    REST_FRAMEWORK={
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "EXCEPTION_HANDLER": "core.exceptions.standard_exception_handler",
        "DEFAULT_THROTTLE_RATES": {
            "api": "2/min",
        },
    },
)
class RateLimitTests(APITestCase):
    def setUp(self):
        cache.clear()
        IPRateThrottle.rate = "2/min"
        self.client.credentials(HTTP_X_API_KEY="dev-safeguard-key")
        self.url = reverse("transaction-list")

    def tearDown(self):
        cache.clear()
        if hasattr(IPRateThrottle, "rate"):
            delattr(IPRateThrottle, "rate")

    def test_returns_429_when_ip_exceeds_rate_limit(self):
        first_response = self.client.get(self.url, REMOTE_ADDR="198.51.100.10")
        second_response = self.client.get(self.url, REMOTE_ADDR="198.51.100.10")
        third_response = self.client.get(self.url, REMOTE_ADDR="198.51.100.10")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(third_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(third_response.data["code"], "rate_limited")

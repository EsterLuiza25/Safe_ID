import json
import logging

from drf_spectacular.utils import OpenApiExample, extend_schema
from drf_spectacular.utils import OpenApiParameter
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.security import HasAPIKey
from core.throttles import IPRateThrottle

from .models import Transaction
from .serializers import (
    AuthorizeTransactionRequestSerializer,
    TransactionReadSerializer,
    TransactionSerializer,
)
from .services.risk_engine import RiskEngine


logger = logging.getLogger("transactions")

API_KEY_HEADER_PARAMETER = OpenApiParameter(
    name="X-API-Key",
    description="Chave de autenticacao da API configurada em SAFEGUARD_API_KEY.",
    required=True,
    type=str,
    location=OpenApiParameter.HEADER,
)


class TransactionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionReadSerializer
    pagination_class = TransactionPagination
    permission_classes = [HasAPIKey]
    throttle_classes = [IPRateThrottle]

    @extend_schema(
        parameters=[
            API_KEY_HEADER_PARAMETER,
            OpenApiParameter(
                name="status",
                description="Filtra por status da transacao: APPROVED ou REJECTED.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="customer_id",
                description="Busca parcial por customer_id.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="page",
                description="Numero da pagina.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="page_size",
                description="Quantidade de itens por pagina, limitado a 100.",
                required=False,
                type=int,
            ),
        ],
        responses={200: TransactionReadSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Transaction.objects.all()
        status_filter = self.request.query_params.get("status")
        customer_id = self.request.query_params.get("customer_id")

        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        if customer_id:
            queryset = queryset.filter(customer_id__icontains=customer_id.strip())

        return queryset


class TransactionDetailView(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionReadSerializer
    lookup_field = "id"
    lookup_url_kwarg = "id"
    permission_classes = [HasAPIKey]
    throttle_classes = [IPRateThrottle]

    @extend_schema(
        parameters=[API_KEY_HEADER_PARAMETER],
        responses={200: TransactionReadSerializer, 404: dict},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AuthorizeTransactionView(APIView):
    serializer_class = AuthorizeTransactionRequestSerializer
    permission_classes = [HasAPIKey]
    throttle_classes = [IPRateThrottle]

    @extend_schema(
        request=AuthorizeTransactionRequestSerializer,
        parameters=[API_KEY_HEADER_PARAMETER],
        responses={201: TransactionSerializer, 400: dict, 403: dict, 429: dict},
        examples=[
            OpenApiExample(
                "Transacao aprovada",
                value={
                    "amount": "250.00",
                    "customer_id": "customer-123",
                    "device_fingerprint": "ios-device-abc",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Transacao rejeitada",
                value={
                    "amount": "15000.00",
                    "customer_id": "customer-123",
                    "device_fingerprint": "blocked-fingerprint-demo",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        decision = RiskEngine().evaluate(
            amount=serializer.validated_data["amount"],
            device_fingerprint=serializer.validated_data["device_fingerprint"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

        transaction = Transaction.objects.create(
            amount=serializer.validated_data["amount"],
            customer_id=serializer.validated_data["customer_id"],
            device_fingerprint=serializer.validated_data["device_fingerprint"],
            ip_address=ip_address,
            risk_score=decision.risk_score,
            status=decision.status,
        )
        transaction.risk_reasons = decision.reasons

        self._log_decision(
            transaction=transaction,
            risk_reasons=decision.reasons,
            user_agent=user_agent,
        )

        response_data = TransactionSerializer(transaction).data

        return Response(response_data, status=http_status.HTTP_201_CREATED)

    def _get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    def _log_decision(self, *, transaction, risk_reasons, user_agent):
        payload = {
            "event": "transaction_authorized",
            "transaction_id": str(transaction.id),
            "customer_id": transaction.customer_id,
            "status": transaction.status,
            "risk_score": transaction.risk_score,
            "risk_reasons": risk_reasons,
            "ip_address": transaction.ip_address,
            "user_agent": user_agent[:180],
        }
        logger.info(json.dumps(payload, ensure_ascii=True))

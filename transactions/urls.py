from django.urls import path

from .views import AuthorizeTransactionView, TransactionDetailView, TransactionListView


urlpatterns = [
    path(
        "transactions/",
        TransactionListView.as_view(),
        name="transaction-list",
    ),
    path(
        "transactions/<uuid:id>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path(
        "transactions/authorize/",
        AuthorizeTransactionView.as_view(),
        name="authorize-transaction",
    ),
]

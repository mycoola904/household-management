from django.urls import path

from .views import (
    AccountCreateView,
    AccountDeleteView,
    AccountDetailView,
    AccountListView,
    AccountTransactionTableView,
    AccountUpdateView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
    TransactionCreateView,
    TransactionDeleteView,
    TransactionListView,
    TransactionUpdateView,
)

app_name = "finance"

urlpatterns = [
    path("accounts/", AccountListView.as_view(), name="account-list"),
    path("accounts/<int:pk>/", AccountDetailView.as_view(), name="account-detail"),
    path("accounts/add/", AccountCreateView.as_view(), name="account-create"),
    path("accounts/<int:pk>/edit/", AccountUpdateView.as_view(), name="account-update"),
    path("accounts/<int:pk>/delete/", AccountDeleteView.as_view(), name="account-delete"),
    path(
        "accounts/<int:pk>/transactions/",
        AccountTransactionTableView.as_view(),
        name="account-transactions",
    ),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/add/", CategoryCreateView.as_view(), name="category-create"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category-update"),
    path("categories/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category-delete"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("transactions/add/", TransactionCreateView.as_view(), name="transaction-create"),
    path("transactions/<int:pk>/edit/", TransactionUpdateView.as_view(), name="transaction-update"),
    path("transactions/<int:pk>/delete/", TransactionDeleteView.as_view(), name="transaction-delete"),
]

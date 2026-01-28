from django.urls import path

from .views import (
    AccountCreateView,
    AccountDeleteView,
    AccountListView,
    AccountUpdateView,
)

app_name = "finance"

urlpatterns = [
    path("accounts/", AccountListView.as_view(), name="account-list"),
    path("accounts/add/", AccountCreateView.as_view(), name="account-create"),
    path("accounts/<int:pk>/edit/", AccountUpdateView.as_view(), name="account-update"),
    path("accounts/<int:pk>/delete/", AccountDeleteView.as_view(), name="account-delete"),
]

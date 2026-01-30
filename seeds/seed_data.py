"""Database seeding scaffold for the Household project.

Populate the helper functions with concrete data rows before running
this script via `python manage.py shell` or a dedicated management command.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from finance.models import Account, Category, Transaction


def _aware_datetime(year: int, month: int, day: int) -> datetime:
    """Return a timezone-aware datetime for stable seeding timestamps."""

    return timezone.make_aware(datetime(year, month, day))


def seed_categories() -> None:
    """Create default categories used by demo transactions."""

    for name in ("Income", "Household", "Interest", "Transfers"):
        Category.objects.update_or_create(name=name)


def seed_accounts() -> None:
    """Create or update Account records required for demo/test scenarios."""

    Account.objects.update_or_create(
        account_number="123456789",
        defaults={
            "name": "Demo Checking",
            "account_type": Account.AccountType.CHECKING,
            "routing_number": "987654321",
            "balance": Decimal("1000.00"),
        },
    )
    Account.objects.update_or_create(
        account_number="987654321",
        defaults={
            "name": "Demo Savings",
            "account_type": Account.AccountType.SAVINGS,
            "routing_number": "123456789",
            "interest_rate": Decimal("1.50"),
            "balance": Decimal("5000.00"),
        },
    )



def seed_transactions() -> None:
    """Attach Transaction rows to existing accounts in an idempotent fashion."""

    checking = Account.objects.get(account_number="123456789")
    savings = Account.objects.get(account_number="987654321")
    income_category = Category.objects.get(name="Income")
    expense_category = Category.objects.get(name="Household")
    interest_category = Category.objects.get(name="Interest")
    transfer_category = Category.objects.get(name="Transfers")

    Transaction.objects.update_or_create(
        account=checking,
        posted_at=_aware_datetime(2026, 1, 15),
        transaction_type=Transaction.TransactionType.INCOME,
        amount=Decimal("2000.00"),
        category=income_category,
        defaults={
            "memo": "Paycheck",
            "is_cleared": True,
        },
    )

    Transaction.objects.update_or_create(
        account=checking,
        posted_at=_aware_datetime(2026, 1, 20),
        transaction_type=Transaction.TransactionType.EXPENSE,
        amount=Decimal("150.00"),
        category=expense_category,
        defaults={
            "memo": "Groceries",
            "is_cleared": True,
        },
    )

    Transaction.objects.update_or_create(
        account=savings,
        posted_at=_aware_datetime(2026, 1, 25),
        transaction_type=Transaction.TransactionType.INCOME,
        amount=Decimal("50.00"),
        category=interest_category,
        defaults={
            "memo": "Interest",
            "is_cleared": True,
        },
    )

    Transaction.objects.update_or_create(
        account=savings,
        posted_at=_aware_datetime(2026, 1, 28),
        transaction_type=Transaction.TransactionType.EXPENSE,
        amount=Decimal("100.00"),
        category=transfer_category,
        defaults={
            "memo": "Transfer to Checking",
            "is_cleared": True,
        },
    )



def main() -> None:
    """Run the full seeding routine inside a single atomic transaction."""
    with transaction.atomic():
        seed_categories()
        seed_accounts()
        seed_transactions()


if __name__ == "__main__":
    # Explicit invocation keeps imports side-effect free.
    main()

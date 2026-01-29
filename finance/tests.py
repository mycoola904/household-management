from __future__ import annotations

from decimal import Decimal
from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Account, Transaction


class AccountModelTests(TestCase):
	def test_checking_requires_routing_number(self):
		"""Checking accounts without routing numbers fail validation."""
		account = Account(
			name="Checking",
			account_number="CHK-1",
			account_type=Account.AccountType.CHECKING,
			routing_number="",
			balance=Decimal("100.00"),
		)

		with self.assertRaises(ValidationError) as ctx:
			account.full_clean()

		self.assertIn("routing_number", ctx.exception.message_dict)

	def test_credit_card_disallows_routing_number(self):
		"""Credit cards reject routing numbers to enforce banking rules."""
		account = Account(
			name="Card",
			account_number="CC-1",
			account_type=Account.AccountType.CREDIT_CARD,
			routing_number="555123456",
			interest_rate=Decimal("18.25"),
			due_date=date(2024, 12, 1),
			balance=Decimal("0.00"),
		)

		with self.assertRaises(ValidationError) as ctx:
			account.full_clean()

		self.assertIn("routing_number", ctx.exception.message_dict)

	def test_savings_requires_interest_rate(self):
		"""Savings accounts must capture an interest rate."""
		account = Account(
			name="High Yield",
			account_number="SAV-1",
			account_type=Account.AccountType.SAVINGS,
			routing_number="123456789",
			balance=Decimal("500.00"),
		)

		with self.assertRaises(ValidationError) as ctx:
			account.full_clean()

		self.assertIn("interest_rate", ctx.exception.message_dict)

	def test_loan_requires_due_date(self):
		"""Loan accounts need a due date for billing cycles."""
		account = Account(
			name="Auto Loan",
			account_number="LOAN-1",
			account_type=Account.AccountType.LOAN,
			interest_rate=Decimal("5.75"),
			balance=Decimal("10000.00"),
		)

		with self.assertRaises(ValidationError) as ctx:
			account.full_clean()

		self.assertIn("due_date", ctx.exception.message_dict)


class TransactionModelTests(TestCase):
	def setUp(self):
		self.account = Account.objects.create(
			name="Checking",
			account_number="CHK-100",
			account_type=Account.AccountType.CHECKING,
			routing_number="111000025",
			balance=Decimal("250.00"),
		)

	def test_signed_amount_debit_and_credit(self):
		"""signed_amount returns negative for expenses and positive otherwise."""
		expense = Transaction(
			account=self.account,
			transaction_type=Transaction.TransactionType.EXPENSE,
			amount=Decimal("42.00"),
		)
		income = Transaction(
			account=self.account,
			transaction_type=Transaction.TransactionType.INCOME,
			amount=Decimal("42.00"),
		)
		transfer = Transaction(
			account=self.account,
			transaction_type=Transaction.TransactionType.TRANSFER,
			amount=Decimal("42.00"),
		)

		self.assertEqual(expense.signed_amount, Decimal("-42.00"))
		self.assertEqual(income.signed_amount, Decimal("42.00"))
		self.assertEqual(transfer.signed_amount, Decimal("42.00"))

	def test_amount_must_be_positive(self):
		"""Transactions cannot be saved with zero or negative amounts."""
		transaction = Transaction(
			account=self.account,
			transaction_type=Transaction.TransactionType.EXPENSE,
			amount=Decimal("0"),
		)

		with self.assertRaises(ValidationError) as ctx:
			transaction.full_clean()

		self.assertIn("amount", ctx.exception.message_dict)


class TransactionListViewTests(TestCase):
	def setUp(self):
		self.account_one = Account.objects.create(
			name="Primary Checking",
			account_number="CHK-1",
			account_type=Account.AccountType.CHECKING,
			routing_number="111000025",
			balance=Decimal("1000.00"),
		)
		self.account_two = Account.objects.create(
			name="Vacation Savings",
			account_number="SAV-1",
			account_type=Account.AccountType.SAVINGS,
			routing_number="222000111",
			interest_rate=Decimal("1.25"),
			balance=Decimal("2500.00"),
			due_date=None,
		)
		self.transaction_one = Transaction.objects.create(
			account=self.account_one,
			transaction_type=Transaction.TransactionType.EXPENSE,
			amount=Decimal("50.00"),
		)
		self.transaction_two = Transaction.objects.create(
			account=self.account_two,
			transaction_type=Transaction.TransactionType.INCOME,
			amount=Decimal("400.00"),
		)

	def test_filters_by_account_id(self):
		"""View narrows queryset to selected account id and preserves filter."""
		url = reverse("finance:transaction-list")
		response = self.client.get(url, {"account": self.account_two.id})

		transactions = list(response.context["transactions"])
		self.assertEqual(transactions, [self.transaction_two])
		self.assertEqual(response.context["selected_account"], str(self.account_two.id))

	def test_ignores_placeholder_account_value(self):
		"""Placeholder values like 'None' should not trigger filtering."""
		url = reverse("finance:transaction-list")
		response = self.client.get(url, {"account": "None"})

		transactions = set(response.context["transactions"])
		self.assertEqual(transactions, {self.transaction_one, self.transaction_two})
		self.assertEqual(response.context["selected_account"], "")

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Account(models.Model):
    class AccountType(models.TextChoices):
        CHECKING = "checking", "Checking"
        SAVINGS = "savings", "Savings"
        CREDIT_CARD = "credit_card", "Credit Card"
        LOAN = "loan", "Loan"

    name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=50, unique=True)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    routing_number = models.CharField(max_length=20, blank=True)
    due_date = models.DateField(blank=True, null=True)
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Annual interest rate as a percentage (e.g., 4.25)",
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_account_type_display()})"

    def clean(self) -> None:
        super().clean()

        routing_required_types = {
            self.AccountType.CHECKING,
            self.AccountType.SAVINGS,
        }
        interest_required_types = {
            self.AccountType.SAVINGS,
            self.AccountType.CREDIT_CARD,
            self.AccountType.LOAN,
        }
        due_date_required_types = {
            self.AccountType.CREDIT_CARD,
            self.AccountType.LOAN,
        }

        errors = {}

        if self.account_type in routing_required_types:
            if not self.routing_number:
                errors["routing_number"] = "Routing number is required for this account type."
        elif self.routing_number:
            errors["routing_number"] = "Routing number is only allowed for checking or savings accounts."

        if self.account_type in interest_required_types:
            if self.interest_rate is None:
                errors["interest_rate"] = "Interest rate is required for this account type."
            elif self.interest_rate < 0:
                errors["interest_rate"] = "Interest rate must be zero or greater."
        elif self.interest_rate is not None:
            errors["interest_rate"] = "Interest rate is only allowed for savings, credit card, or loan accounts."

        if self.account_type in due_date_required_types:
            if not self.due_date:
                errors["due_date"] = "Due date is required for this account type."
        elif self.due_date:
            errors["due_date"] = "Due date is only allowed for credit card or loan accounts."

        if errors:
            raise ValidationError(errors)


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        EXPENSE = "expense", "Expense"
        INCOME = "income", "Income"
        CHARGE = "charge", "Charge"
        PAYMENT = "payment", "Payment"
        TRANSFER = "transfer", "Transfer"
        ADJUSTMENT = "adjustment", "Adjustment"

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    memo = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    posted_at = models.DateTimeField(default=timezone.now)
    is_cleared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-posted_at", "-id"]

    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()} {self.amount} for {self.account.name}"

    @property
    def signed_amount(self):
        debit_types = {self.TransactionType.EXPENSE, self.TransactionType.PAYMENT}
        credit_types = {self.TransactionType.INCOME, self.TransactionType.CHARGE}
        if self.transaction_type in debit_types:
            return -self.amount
        if self.transaction_type in credit_types:
            return self.amount
        # transfers & adjustments treated as positive value; caller decides how to display
        return self.amount

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.amount is None or self.amount <= 0:
            errors["amount"] = "Amount must be greater than zero."

        if errors:
            raise ValidationError(errors)

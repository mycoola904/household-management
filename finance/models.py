from django.db import models


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
	balance = models.DecimalField(max_digits=12, decimal_places=2)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:
		return f"{self.name} ({self.get_account_type_display()})"

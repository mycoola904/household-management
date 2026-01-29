from django.contrib import admin

from .forms import AccountForm, TransactionForm
from .models import Account, Transaction


class TransactionInline(admin.TabularInline):
	model = Transaction
	extra = 0
	fields = ("posted_at", "transaction_type", "amount", "is_cleared")
	readonly_fields = ("posted_at",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	form = AccountForm
	inlines = (TransactionInline,)
	list_display = (
		"name",
		"account_type",
		"account_number",
		"balance",
		"interest_rate",
		"due_date",
	)
	list_filter = ("account_type",)
	search_fields = ("name", "account_number", "routing_number")
	fieldsets = (
		(
			None,
			{
				"fields": (
					"name",
					"account_number",
					"account_type",
					"routing_number",
					"interest_rate",
					"due_date",
					"balance",
				)
			},
		),
	)

	class Media:
		js = ("finance/admin/account_form.js",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	form = TransactionForm
	list_display = (
		"posted_at",
		"account",
		"transaction_type",
		"amount",
		"is_cleared",
	)
	list_filter = ("transaction_type", "account", "is_cleared")
	search_fields = ("memo", "reference")
	autocomplete_fields = ("account",)
	readonly_fields = ("created_at", "updated_at")

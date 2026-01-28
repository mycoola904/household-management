from django.contrib import admin

from .forms import AccountForm
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	form = AccountForm
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

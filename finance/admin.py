from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	list_display = ("name", "account_type", "account_number", "balance", "due_date")
	list_filter = ("account_type",)
	search_fields = ("name", "account_number", "routing_number")

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View

from .forms import AccountForm, TransactionForm
from .models import Account, Transaction


class AccountListView(View):
	template_name = "finance/account_list.html"
	partial_name = "finance/partials/account_rows.html"

	def get(self, request, *args, **kwargs):
		accounts = Account.objects.all()
		context = {"accounts": accounts}
		if request.htmx:
			return render(request, self.partial_name, context)
		return render(request, self.template_name, context)


class AccountCreateView(View):
	form_class = AccountForm
	template_name = "finance/partials/account_form.html"

	def get(self, request, *args, **kwargs):
		form = self.form_class()
		context = {
			"form": form,
			"title": "Add Account",
			"action": reverse("finance:account-create"),
		}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			form.save()
			response = HttpResponse(status=204)
			response["HX-Trigger"] = "{\"accountsChanged\": {}, \"closeAccountModal\": {}}"
			return response
		context = {
			"form": form,
			"title": "Add Account",
			"action": reverse("finance:account-create"),
		}
		return render(request, self.template_name, context, status=400)


class AccountUpdateView(View):
	form_class = AccountForm
	template_name = "finance/partials/account_form.html"

	def get_object(self, pk):
		return get_object_or_404(Account, pk=pk)

	def get(self, request, pk, *args, **kwargs):
		account = self.get_object(pk)
		form = self.form_class(instance=account)
		context = {
			"form": form,
			"title": f"Edit {account.name}",
			"action": reverse("finance:account-update", args=[account.pk]),
		}
		return render(request, self.template_name, context)

	def post(self, request, pk, *args, **kwargs):
		account = self.get_object(pk)
		form = self.form_class(request.POST, instance=account)
		if form.is_valid():
			form.save()
			response = HttpResponse(status=204)
			response["HX-Trigger"] = "{\"accountsChanged\": {}, \"closeAccountModal\": {}}"
			return response
		context = {
			"form": form,
			"title": f"Edit {account.name}",
			"action": reverse("finance:account-update", args=[account.pk]),
		}
		return render(request, self.template_name, context, status=400)


class AccountDeleteView(View):
	template_name = "finance/partials/account_confirm_delete.html"

	def get_object(self, pk):
		return get_object_or_404(Account, pk=pk)

	def get(self, request, pk, *args, **kwargs):
		account = self.get_object(pk)
		context = {
			"account": account,
			"action": reverse("finance:account-delete", args=[account.pk]),
		}
		return render(request, self.template_name, context)

	def post(self, request, pk, *args, **kwargs):
		account = self.get_object(pk)
		account.delete()
		response = HttpResponse(status=204)
		response["HX-Trigger"] = "{\"accountsChanged\": {}, \"closeAccountModal\": {}}"
		return response


class TransactionListView(View):
	template_name = "finance/transaction_list.html"
	partial_name = "finance/partials/transaction_rows.html"

	def get_queryset(self, request):
		qs = Transaction.objects.select_related("account").all()
		raw_account_id = request.GET.get("account")
		account_id = raw_account_id if raw_account_id not in (None, "", "None") else None
		if account_id:
			qs = qs.filter(account_id=account_id)
		return qs, raw_account_id if account_id else ""

	def get(self, request, *args, **kwargs):
		transactions, selected_account = self.get_queryset(request)
		context = {
			"transactions": transactions,
			"accounts": Account.objects.all(),
			"selected_account": selected_account or "",
		}
		if request.htmx:
			return render(request, self.partial_name, context)
		return render(request, self.template_name, context)


class TransactionCreateView(View):
	form_class = TransactionForm
	template_name = "finance/partials/transaction_form.html"

	def get_initial(self, request):
		initial = {}
		account_id = request.GET.get("account")
		if account_id:
			initial["account"] = account_id
		return initial

	def get(self, request, *args, **kwargs):
		form = self.form_class(initial=self.get_initial(request))
		context = {
			"form": form,
			"title": "Add Transaction",
			"action": reverse("finance:transaction-create"),
		}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			form.save()
			response = HttpResponse(status=204)
			response["HX-Trigger"] = "{\"transactionsChanged\": {}, \"closeAccountModal\": {}}"
			return response
		context = {
			"form": form,
			"title": "Add Transaction",
			"action": reverse("finance:transaction-create"),
		}
		return render(request, self.template_name, context, status=400)


class TransactionUpdateView(View):
	form_class = TransactionForm
	template_name = "finance/partials/transaction_form.html"

	def get_object(self, pk):
		return get_object_or_404(Transaction, pk=pk)

	def get(self, request, pk, *args, **kwargs):
		transaction = self.get_object(pk)
		form = self.form_class(instance=transaction)
		context = {
			"form": form,
			"title": "Edit Transaction",
			"action": reverse("finance:transaction-update", args=[transaction.pk]),
		}
		return render(request, self.template_name, context)

	def post(self, request, pk, *args, **kwargs):
		transaction = self.get_object(pk)
		form = self.form_class(request.POST, instance=transaction)
		if form.is_valid():
			form.save()
			response = HttpResponse(status=204)
			response["HX-Trigger"] = "{\"transactionsChanged\": {}, \"closeAccountModal\": {}}"
			return response
		context = {
			"form": form,
			"title": "Edit Transaction",
			"action": reverse("finance:transaction-update", args=[transaction.pk]),
		}
		return render(request, self.template_name, context, status=400)


class TransactionDeleteView(View):
	template_name = "finance/partials/transaction_confirm_delete.html"

	def get_object(self, pk):
		return get_object_or_404(Transaction, pk=pk)

	def get(self, request, pk, *args, **kwargs):
		transaction = self.get_object(pk)
		context = {
			"transaction": transaction,
			"action": reverse("finance:transaction-delete", args=[transaction.pk]),
		}
		return render(request, self.template_name, context)

	def post(self, request, pk, *args, **kwargs):
		transaction = self.get_object(pk)
		transaction.delete()
		response = HttpResponse(status=204)
		response["HX-Trigger"] = "{\"transactionsChanged\": {}, \"closeAccountModal\": {}}"
		return response

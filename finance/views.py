import json
from calendar import monthrange
from datetime import date, datetime, time

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.db.models import ProtectedError

from .forms import AccountForm, CategoryForm, TransactionForm
from .models import Account, Category, Transaction


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


class CategoryListView(View):
	template_name = "finance/category_list.html"
	partial_name = "finance/partials/category_rows.html"

	def get(self, request, *args, **kwargs):
		categories = Category.objects.order_by("name")
		context = {"categories": categories}
		if request.htmx:
			return render(request, self.partial_name, context)
		return render(request, self.template_name, context)


class CategoryFormMixin:
	form_class = CategoryForm
	template_name = "finance/partials/category_form.html"

	def _select_id(self, request):
		return request.GET.get("select_id") or request.POST.get("select_id")

	def _is_inline(self, request):
		flag = request.GET.get("inline") or request.POST.get("inline")
		return flag == "1"

	def _target(self, request, select_id):
		if self._is_inline(request) and select_id:
			return f"#{select_id}-inline-form"
		return "#modal-body"

	def _context(self, request, form, *, title, action):
		select_id = self._select_id(request)
		inline = self._is_inline(request)
		return {
			"form": form,
			"title": title,
			"action": action,
			"select_id": select_id,
			"inline": inline,
			"target": self._target(request, select_id),
		}

	def _success_response(self, request, detail):
		payload = {"categoriesChanged": detail}
		if not self._is_inline(request):
			payload["closeAccountModal"] = {}
		response = HttpResponse(status=204)
		response["HX-Trigger"] = json.dumps(payload)
		return response


class CategoryCreateView(CategoryFormMixin, View):
	def get(self, request, *args, **kwargs):
		form = self.form_class()
		context = self._context(
			request,
			form,
			title="Add Category",
			action=reverse("finance:category-create"),
		)
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			category = form.save()
			select_id = self._select_id(request)
			return self._success_response(
				request,
				{
					"action": "created",
					"id": category.id,
					"name": category.name,
					"selectId": select_id,
				},
			)
		context = self._context(
			request,
			form,
			title="Add Category",
			action=reverse("finance:category-create"),
		)
		return render(request, self.template_name, context, status=400)


class CategoryUpdateView(CategoryFormMixin, View):
	def get_object(self, pk):
		return get_object_or_404(Category, pk=pk)

	def get(self, request, pk, *args, **kwargs):
		category = self.get_object(pk)
		form = self.form_class(instance=category)
		context = self._context(
			request,
			form,
			title=f"Edit {category.name}",
			action=reverse("finance:category-update", args=[category.pk]),
		)
		return render(request, self.template_name, context)

	def post(self, request, pk, *args, **kwargs):
		category = self.get_object(pk)
		form = self.form_class(request.POST, instance=category)
		if form.is_valid():
			category = form.save()
			select_id = self._select_id(request)
			return self._success_response(
				request,
				{
					"action": "updated",
					"id": category.id,
					"name": category.name,
					"selectId": select_id,
				},
			)
		context = self._context(
			request,
			form,
			title=f"Edit {category.name}",
			action=reverse("finance:category-update", args=[category.pk]),
		)
		return render(request, self.template_name, context, status=400)


class CategoryDeleteView(View):
	template_name = "finance/partials/category_confirm_delete.html"

	def get_object(self, pk):
		return get_object_or_404(Category, pk=pk)

	def get(self, request, pk, *args, **kwargs):
		category = self.get_object(pk)
		context = {
			"category": category,
			"action": reverse("finance:category-delete", args=[category.pk]),
			"target": "#modal-body",
			"error": None,
		}
		return render(request, self.template_name, context)

	def post(self, request, pk, *args, **kwargs):
		category = self.get_object(pk)
		try:
			category.delete()
		except ProtectedError:
			context = {
				"category": category,
				"action": reverse("finance:category-delete", args=[category.pk]),
				"error": "Cannot delete a category while it is used by transactions.",
				"target": "#modal-body",
			}
			return render(request, self.template_name, context, status=400)
		payload = {
			"categoriesChanged": {"action": "deleted", "id": category.id},
			"closeAccountModal": {},
		}
		response = HttpResponse(status=204)
		response["HX-Trigger"] = json.dumps(payload)
		return response


class AccountDetailView(View):
	template_name = "finance/account_detail.html"

	def get(self, request, pk, *args, **kwargs):
		account = get_object_or_404(Account, pk=pk)
		routing_types = {
			Account.AccountType.CHECKING,
			Account.AccountType.SAVINGS,
		}
		interest_types = {
			Account.AccountType.SAVINGS,
			Account.AccountType.CREDIT_CARD,
			Account.AccountType.LOAN,
		}
		due_date_types = {
			Account.AccountType.CREDIT_CARD,
			Account.AccountType.LOAN,
		}
		context = {
			"account": account,
			"transactions_url": reverse("finance:account-transactions", args=[account.pk]),
			"show_routing": account.account_type in routing_types,
			"show_interest": account.account_type in interest_types,
			"show_due_date": account.account_type in due_date_types,
		}
		return render(request, self.template_name, context)


class AccountTransactionTableView(View):
	template_name = "finance/partials/transaction_table.html"

	def _resolve_month(self, request):
		month_param = request.GET.get("month")
		default_month = timezone.localdate().replace(day=1)
		if month_param:
			try:
				year_str, month_str = month_param.split("-")
				return date(int(year_str), int(month_str), 1)
			except (ValueError, TypeError):
				return default_month
		return default_month

	def _month_bounds(self, first_day: date):
		last_day = monthrange(first_day.year, first_day.month)[1]
		end_day = date(first_day.year, first_day.month, last_day)
		tz = timezone.get_current_timezone()
		start_dt = timezone.make_aware(datetime.combine(first_day, time.min), tz)
		end_dt = timezone.make_aware(datetime.combine(end_day, time.max), tz)
		return start_dt, end_dt

	def _shift_month(self, first_day: date, delta: int) -> date:
		month_index = first_day.month - 1 + delta
		year = first_day.year + month_index // 12
		month = month_index % 12 + 1
		return date(year, month, 1)

	def get(self, request, pk, *args, **kwargs):
		account = get_object_or_404(Account, pk=pk)
		current_month = self._resolve_month(request)
		start_dt, end_dt = self._month_bounds(current_month)
		transactions = (
			Transaction.objects.select_related("account", "category")
			.filter(account=account, posted_at__range=(start_dt, end_dt))
			.order_by("-posted_at", "-id")
		)
		context = {
			"account": account,
			"transactions": transactions,
			"month_label": current_month.strftime("%B %Y"),
			"current_month": current_month.strftime("%Y-%m"),
			"prev_month": self._shift_month(current_month, -1).strftime("%Y-%m"),
			"next_month": self._shift_month(current_month, 1).strftime("%Y-%m"),
			"transactions_url": reverse("finance:account-transactions", args=[account.pk]),
		}
		return render(request, self.template_name, context)


class TransactionListView(View):
	template_name = "finance/transaction_list.html"
	partial_name = "finance/partials/transaction_rows.html"

	def get_queryset(self, request):
		qs = Transaction.objects.select_related("account", "category").all()
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
			transaction = form.save()
			account_id = transaction.account_id
			response = HttpResponse(status=204)
			response["HX-Trigger"] = json.dumps(
				{
					"transactionsChanged": {"accounts": [account_id]},
					"closeAccountModal": {},
				}
			)
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
		old_account_id = transaction.account_id
		form = self.form_class(request.POST, instance=transaction)
		if form.is_valid():
			transaction = form.save()
			account_ids = {old_account_id, transaction.account_id}
			account_ids.discard(None)
			response = HttpResponse(status=204)
			response["HX-Trigger"] = json.dumps(
				{
					"transactionsChanged": {"accounts": list(account_ids)},
					"closeAccountModal": {},
				}
			)
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
		account_id = transaction.account_id
		transaction.delete()
		response = HttpResponse(status=204)
		payload = {
			"transactionsChanged": {"accounts": [account_id] if account_id else []},
			"closeAccountModal": {},
		}
		response["HX-Trigger"] = json.dumps(payload)
		return response

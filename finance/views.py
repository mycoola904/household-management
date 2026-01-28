from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View

from .forms import AccountForm
from .models import Account


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

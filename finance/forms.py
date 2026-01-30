from django import forms
from django.utils import timezone

from .models import Account, Category, Transaction


def _apply_tailwind_classes(form):
    widget_classes = {
        "select": "select select-bordered",
        "textarea": "textarea textarea-bordered",
        "checkboxinput": "checkbox checkbox-sm",
    }
    for field in form.fields.values():
        widget = field.widget
        widget_type = widget.__class__.__name__.lower()
        css_class = widget_classes.get(widget_type, "input input-bordered")
        existing = widget.attrs.get("class", "")
        widget.attrs["class"] = f"{existing} {css_class}".strip()


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            "name",
            "account_number",
            "account_type",
            "routing_number",
            "interest_rate",
            "due_date",
            "balance",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_tailwind_classes(self)

        self.fields["interest_rate"].widget.attrs.update({"step": "0.01", "min": "0"})
        self.fields["balance"].widget.attrs.update({"step": "0.01"})
        self.fields["due_date"].widget.input_type = "date"

    def clean(self):
        cleaned_data = super().clean()

        account_type = cleaned_data.get("account_type")
        routing_number = cleaned_data.get("routing_number")
        interest_rate = cleaned_data.get("interest_rate")
        due_date = cleaned_data.get("due_date")

        routing_required_types = {
            Account.AccountType.CHECKING,
            Account.AccountType.SAVINGS,
        }
        interest_required_types = {
            Account.AccountType.SAVINGS,
            Account.AccountType.CREDIT_CARD,
            Account.AccountType.LOAN,
        }
        due_date_required_types = {
            Account.AccountType.CREDIT_CARD,
            Account.AccountType.LOAN,
        }

        if account_type in routing_required_types and not routing_number:
            self.add_error(
                "routing_number",
                "Routing number is required for checking or savings accounts.",
            )
        if account_type not in routing_required_types and routing_number:
            self.add_error(
                "routing_number",
                "Routing number is only allowed for checking or savings accounts.",
            )
        if account_type in interest_required_types and interest_rate is None:
            self.add_error(
                "interest_rate",
                "Interest rate is required for this account type.",
            )
        if account_type not in interest_required_types and interest_rate is not None:
            self.add_error(
                "interest_rate",
                "Interest rate is only allowed for savings, credit card, or loan accounts.",
            )
        if account_type in due_date_required_types and not due_date:
            self.add_error(
                "due_date",
                "Due date is required for this account type.",
            )
        if account_type not in due_date_required_types and due_date:
            self.add_error(
                "due_date",
                "Due date is only allowed for credit card or loan accounts.",
            )

        return cleaned_data


class TransactionForm(forms.ModelForm):
    CREDIT_ACCOUNT_TYPES = {
        Account.AccountType.CREDIT_CARD,
        Account.AccountType.LOAN,
    }
    CREDIT_ALLOWED_TRANSACTION_TYPES = {
        Transaction.TransactionType.PAYMENT,
        Transaction.TransactionType.CHARGE,
    }

    class Meta:
        model = Transaction
        fields = (
            "account",
            "transaction_type",
            "amount",
            "category",
            "memo",
            "reference",
            "posted_at",
            "is_cleared",
        )
        widgets = {
            "posted_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_tailwind_classes(self)
        self.fields["amount"].widget.attrs.update({"step": "0.01", "min": "0"})
        self.fields["category"].queryset = self._category_queryset()
        self.fields["category"].empty_label = "Select category"
        self.fields["category"].widget.attrs.setdefault("data-category-select", "true")
        self._limit_transaction_type_choices()

        posted_at = self.initial.get("posted_at") or (
            self.instance.posted_at if self.instance.pk else timezone.now()
        )
        if posted_at:
            self.initial["posted_at"] = posted_at.strftime("%Y-%m-%dT%H:%M")

    def _limit_transaction_type_choices(self):
        field = self.fields["transaction_type"]
        account = self._infer_account_for_type_limit()
        if account and account.account_type in self.CREDIT_ACCOUNT_TYPES:
            field.choices = [
                choice
                for choice in Transaction.TransactionType.choices
                if choice[0] in self.CREDIT_ALLOWED_TRANSACTION_TYPES
            ]
        else:
            field.choices = list(Transaction.TransactionType.choices)

    def _infer_account_for_type_limit(self):
        if self.instance.pk and self.instance.account_id:
            return self.instance.account
        if "account" in self.initial:
            initial_value = self.initial["account"]
            if isinstance(initial_value, Account):
                return initial_value
            return Account.objects.filter(pk=initial_value).first()
        bound_value = self.data.get(self.add_prefix("account")) if self.data else None
        if bound_value:
            return Account.objects.filter(pk=bound_value).first()
        return None

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def _category_queryset(self):
        return Category.objects.filter(is_active=True).order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get("account")
        transaction_type = cleaned_data.get("transaction_type")
        if (
            account
            and account.account_type in self.CREDIT_ACCOUNT_TYPES
            and transaction_type
            and transaction_type not in self.CREDIT_ALLOWED_TRANSACTION_TYPES
        ):
            self.add_error(
                "transaction_type",
                "Credit card and loan accounts support only Payment or Charge transactions.",
            )
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_tailwind_classes(self)

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        return " ".join(name.split())

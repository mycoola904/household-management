from django import forms

from .models import Account


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
        widget_classes = {
            "select": "select select-bordered",
            "textarea": "textarea textarea-bordered",
        }
        for name, field in self.fields.items():
            widget_type = field.widget.__class__.__name__.lower()
            css_class = widget_classes.get(widget_type, "input input-bordered")
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()

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

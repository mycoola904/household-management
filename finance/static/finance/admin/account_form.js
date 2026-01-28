(function () {
    function $(selector) {
        return document.querySelector(selector);
    }

    function toggleField(fieldName, shouldShow) {
        var row = document.querySelector('.field-' + fieldName);
        if (!row) {
            return;
        }
        row.style.display = shouldShow ? '' : 'none';
        var input = $('#id_' + fieldName);
        if (input) {
            if (shouldShow) {
                input.removeAttribute('disabled');
                input.setAttribute('required', 'required');
            } else {
                input.setAttribute('disabled', 'disabled');
                input.removeAttribute('required');
                if (input.type !== 'hidden') {
                    input.value = '';
                }
            }
        }
    }

    function applyAccountTypeRules() {
        var accountTypeSelect = $('#id_account_type');
        if (!accountTypeSelect) {
            return;
        }
        var value = accountTypeSelect.value;
        var needsRouting = ['checking', 'savings'];
        var needsInterest = ['savings', 'credit_card', 'loan'];
        var needsDueDate = ['credit_card', 'loan'];

        toggleField('routing_number', needsRouting.indexOf(value) !== -1);
        toggleField('interest_rate', needsInterest.indexOf(value) !== -1);
        toggleField('due_date', needsDueDate.indexOf(value) !== -1);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var accountTypeSelect = $('#id_account_type');
        if (!accountTypeSelect) {
            return;
        }
        applyAccountTypeRules();
        accountTypeSelect.addEventListener('change', applyAccountTypeRules);
    });
})();

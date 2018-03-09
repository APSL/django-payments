from __future__ import unicode_literals
from django import forms

from ..forms import PaymentForm


class AddonPaymentsForm(PaymentForm):

    def __init__(self, payment_fields, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field, data in payment_fields.items():
            self.fields[field] = forms.CharField(
                initial=data, widget=forms.HiddenInput(attrs={'id': 'id_{}'.format(field)}))

    def clean(self):
        cleaned_data = super(AddonPaymentsForm, self).clean()
        return cleaned_data

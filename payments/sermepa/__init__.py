from __future__ import unicode_literals

from decimal import Decimal, ROUND_HALF_UP

from django.urls import reverse

from ..core import BasicProvider, get_base_url

from .forms import SermepaForm


class SermepaProvider(BasicProvider):
    form_class = SermepaForm

    def __init__(self, merchant_code, terminal, currency, action, **kwargs):
        self.merchant_code = merchant_code
        self.terminal = terminal
        self.currency = currency
        self.action = action
        super(SermepaProvider, self).__init__(**kwargs)

    def get_merchant_parameters(self, payment):
        mp = {
            'DS_MERCHANT_MERCHANTDATA': payment.pk,
            'DS_MERCHANT_MERCHANTCODE': self.merchant_code,
            'DS_MERCHANT_TERMINAL': self.terminal,
            'DS_MERCHANT_TRANSACTIONTYPE': '0',
            'DS_MERCHANT_CURRENCY': self.currency,
            'DS_MERCHANT_AMOUNT': self.get_amount(payment),
            'DS_MERCHANT_ORDER': payment.merchant_order,
            'DS_MERCHANT_URLOK': payment.get_success_url(),
            'DS_MERCHANT_URLKO': payment.get_failure_url(),
            'DS_MERCHANT_MERCHANTURL': '{}{}'.format(get_base_url(), reverse('sermepa_ipn')),
        }
        return mp

    def get_amount(self, payment):
        """Amount in cents"""
        return int(payment.total.quantize(Decimal('0.01'), ROUND_HALF_UP) * 100)

    def get_form(self, payment, data=None):
        return SermepaForm(action=self.action,
                           method=self._method,
                           merchant_parameters=self.get_merchant_parameters(payment))

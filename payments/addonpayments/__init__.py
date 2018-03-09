from __future__ import unicode_literals

import json

from addonpayments.hpp.hpp import Hpp
from addonpayments.hpp.payment.requests import PaymentRequest
from django.template.response import TemplateResponse
from django.utils.translation import get_language

from .forms import AddonPaymentsForm
from .. import PaymentStatus
from ..core import BasicProvider


class AddonPaymentsProvider(BasicProvider):
    form_class = AddonPaymentsForm
    _endpoint = 'https://hpp.sandbox.addonpayments.com/pay'

    def __init__(self, merchant_id, secret_key, endpoint=_endpoint, **kwargs):
        self.hpp = Hpp(secret_key)
        self.endpoint = endpoint
        self.merchant_id = merchant_id
        super(AddonPaymentsProvider, self).__init__(**kwargs)

    def get_hidden_fields(self, payment):
        current_language = get_language()
        request = PaymentRequest(
            merchant_id=self.merchant_id,
            amount=int(float(payment.total) * 100),
            currency=payment.currency,
            auto_settle_flag=True,
            merchant_response_url=self.get_return_url(payment),
            hpp_lang=current_language,
            hpp_version=2
        )
        jsondata_form = self.hpp.request_to_json(request, False)
        return json.loads(jsondata_form)

    def get_form(self, payment, data=None):
        return AddonPaymentsForm(payment_fields=self.get_hidden_fields(payment), action=self.get_action(payment),
                                 method=self._method)

    def get_action(self, payment):
        return self.endpoint

    def process_data(self, payment, request):
        if payment.status == PaymentStatus.WAITING:
            # If the payment is not in waiting state, we probably have a page reload.
            # We should neither throw 404 nor alter the payment again in such case.
            result = request.POST.get('RESULT')
            if result and result == '00':
                payment.captured_amount = payment.total
                payment.change_status(PaymentStatus.CONFIRMED)
                return TemplateResponse(
                    request, 'payments/addonpayments/success.html', context={
                        'return_url': payment.get_success_url()
                    })
            else:
                # XXX: We should recognize AUTHENTICATED and REGISTERED in the future.
                payment.change_status(PaymentStatus.REJECTED)
                return TemplateResponse(
                    request, 'payments/addonpayments/failure.html', context={
                        'return_url': payment.get_failure_url()
                    })
        return TemplateResponse(
            request, 'payments/addonpayments/success.html', context={
                'return_url': payment.get_success_url()
            })

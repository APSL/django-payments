from __future__ import unicode_literals

from sermepa.forms import SermepaPaymentForm

from ..forms import PaymentForm


class SermepaForm(SermepaPaymentForm, PaymentForm):
    pass

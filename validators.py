from django.core.exceptions import ValidationError
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext as _


class PhoneValidator:
    message = _('Enter a valid phone number.')
    code = "invalid"
    phone_regex = _lazy_re_compile(r"^((\+213)|(00213)|(0))(6|7|5)[0-9]{8}$")

    def __init__(self, message=None, code=None, allowlist=None):
        if message is not None:
            self.message = message

    def __call__(self, value):
        if not self.phone_regex.match(value):
            raise ValidationError(self.message, code=self.code, params={"value": value})

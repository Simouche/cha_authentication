from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Func
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords

from authentication.utils import generate_otp
from authentication.managers import DeletableManager

User = get_user_model()
do_nothing = models.DO_NOTHING
cascade = models.CASCADE


class MultiToken(Token):
    user = models.ForeignKey(
        get_user_model(), related_name='tokens',
        on_delete=models.CASCADE, verbose_name="User"
    )
    device_name = models.CharField(max_length=255, blank=True)


class Verification(models.Model):
    email = models.EmailField(_("email address"), blank=True, null=True)
    phone = models.CharField(_("phone"), max_length=150, null=True, blank=True)
    otp = models.TextField(max_length=10, unique=True, default=generate_otp, db_index=True)
    expired = models.BooleanField(default=False)

    def send(self) -> None:
        if self.expired:
            return

        if self.email and 'dummy' not in self.email:
            pass

        if self.phone:
            pass

    @property
    def reset_link(self) -> str:
        return f"https://app.theschool.pro/password/reset/?otp={self.otp}"

    def build_email(self) -> EmailMultiAlternatives:
        invitation_html = render_to_string("mail/password_reset.html",
                                           {"link": self.reset_link, "otp": self.otp})
        text_content = f'You requested a password reset, please follow the link {self.reset_link}'
        msg = EmailMultiAlternatives(_('Password reset'), text_content, "contact@theschool.pro",
                                     [self.email])
        msg.attach_alternative(invitation_html, "text/html")
        return msg

    def build_sms(self) -> str:

        sms = f"Vous avez demander la reinitialisation de votre mot de passe, votre code est" \
              f" :\n{self.otp} \n"
        return sms

    class Meta:
        verbose_name = _("Verification")
        verbose_name_plural = _("Verifications")
        abstract = True

class BaseModel(models.Model):
    """
    Base Model with creation and update timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HistoryModel(BaseModel):
    """
    Base Model with history.
    """
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class DeletableModel(BaseModel):
    """
    Soft delete Base model
    """
    visible = models.BooleanField(default=True)

    objects = DeletableManager()

    def delete(self, using=None, keep_parents=False):
        self.visible = False
        self.save()
        # TODO: 26 / 06 / 2022 add force delete

    class Meta:
        abstract = True


class Round(Func):
    """
    aggregation function rounds the decimal (float/double) to 2 decimal digits.
    """

    function = 'ROUND'
    arity = 2

    def __ror__(self, other):
        pass

    def __rand__(self, other):
        pass


class Month(Func):
    """
    aggregation function extracts the month number from the database date or timestamp field.
    """

    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()

    def __rand__(self, other):
        pass

    def __ror__(self, other):
        pass

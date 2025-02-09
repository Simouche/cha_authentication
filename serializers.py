from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.db.models import Q
from django.db.transaction import atomic
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.serializers import ModelSerializer, Serializer, EmailField, CharField, ValidationError
from django.utils.translation import gettext as _

from authentication.utils import get_verification_model
from authentication.validators import PhoneValidator

Verification = get_verification_model()
User = get_user_model()

class AdvancedAuthTokenSerializer(AuthTokenSerializer):
    username = CharField(
        label=_("Username"),
        write_only=True,
        required=False,
    )
    password = CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        required=False,
    )
    access_code = CharField(
        label=_("Access Code"),
        write_only=True,
        required=False,
    )

    def validate(self, attrs):
        access_code = attrs.get('access_code')

        if access_code:
            try:
                user = User.objects.get(access_code=access_code)
                attrs['user'] = user
                return attrs
            except User.DoesNotExist:
                msg = _('Unable to log in with provided credentials.')
                raise ValidationError(msg, code='authorization')
        else:
            return super().validate(attrs)

    class Meta:
        extra_kwargs = {
            "username": {"required": False},
            "password": {"required": False},
            "access_code": {"required": False},
        }


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name')


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class RequestPasswordResetSerializer(Serializer):
    email = EmailField(required=False)
    phone = CharField(required=False, validators=(PhoneValidator(),))

    def validate(self, attrs):
        if not attrs.get('email') and not attrs.get('phone'):
            raise ValidationError(_('You should provide either email or phone'))

        if attrs.get('email') and attrs.get('phone'):
            raise ValidationError(_('You should provide either email or phone, not both.'))

        return super().validate(attrs)

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def create(self, validated_data):
        if validated_data.get('email'):
            if not User.objects.filter(email=validated_data.get('email')).exists():
                raise ValidationError(_("User doesn't exist."))

            if Verification.objects.filter(Q(email=validated_data.get('email')), expired=False).exists():
                instance = Verification.objects.filter(Q(email=validated_data.get('email'))).first()
            else:
                instance = Verification.objects.create(email=validated_data.get('email'))
        else:
            if not User.objects.filter(phone=validated_data.get('phone')).exists():
                raise ValidationError(_("User doesn't exist."))

            if Verification.objects.filter(Q(phone=validated_data.get('phone')), expired=False).exists():
                instance = Verification.objects.filter(Q(phone=validated_data.get('phone'))).first()
            else:
                instance = Verification.objects.create(phone=validated_data.get('phone'))
        instance.send()
        return instance


class PasswordResetSerializer(Serializer):
    otp = CharField(required=True)
    password = CharField(required=True)
    confirm_password = CharField(required=True)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            msg = _("passwords don't match")
            raise ValidationError(msg, code="unmatch")

        try:
            verification = Verification.objects.get(otp=attrs.get('otp'))
            if verification.expired:
                raise ValidationError(_('Password reset expired'))
            self.verification = verification
        except Verification.DoesNotExist:
            raise ValidationError(_('Password Reset Request not found'))

        return attrs

    def update(self, instance, validated_data):
        return self.create(validated_data)

    @atomic()
    def create(self, validated_data):
        if self.verification.email:
            user = User.objects.get(email=self.verification.email)
        else:
            user = User.objects.get(phone=self.verification.phone)
        user.set_password(validated_data.get('password'))
        user.save()
        self.verification.expired = True
        self.verification.save()
        return user


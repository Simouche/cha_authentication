"""
adapted from django's ModelBackend, just adding the possibility of authenticating with different fields (phone, email)
 in addition to the USERNAME field.
"""

from urllib.parse import parse_qs

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions

from authentication.models import MultiToken

UserModel = get_user_model()


class PhoneBackend(ModelBackend):
    def authenticate(self, request, username: str = None, password: str = None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(phone__iexact=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


async def get_websocket_authorization_query(scope):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = parse_qs(scope['query_string']).get(b'Authorization', [b''])[0]
    return auth


class WebsocketMultiTokenAuthentication:
    keyword = 'Token'
    model = MultiToken

    async def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    async def authenticate_websocket(self, scope):
        auth = (await get_websocket_authorization_query(scope)).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return await self.authenticate_credentials(token)

    async def authenticate_credentials(self, key):
        model = await self.get_model()
        try:
            token = await model.objects.select_related('user').aget(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return token.user, token

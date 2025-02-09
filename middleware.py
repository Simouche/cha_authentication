from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions

from authentication.contexts import CurrentApplicationContext


class CurrentContextMiddleware(MiddlewareMixin):
    """
    Expose request to other layers of the application (models, signals... etc).

    This middleware sets request as a local context/thread variable, making it
    available to the model-level utilities to allow tracking of the authenticated user.
    """

    def process_request(self, request):
        CurrentApplicationContext.context.request = request
        CurrentApplicationContext.context.referrer = request.META.get("HTTP_REFERER")
        if request.user.is_authenticated:
            CurrentApplicationContext.context.user = request.user

    def process_response(self, request, response):
        if hasattr(CurrentApplicationContext.context, "request"):
            del CurrentApplicationContext.context.request
        if hasattr(CurrentApplicationContext.context, "referrer"):
            del CurrentApplicationContext.context.referrer
        if hasattr(CurrentApplicationContext.context, "user"):
            del CurrentApplicationContext.context.user
        return response


class DRFTokenAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        from authentication.authentication import MultiTokenAuthentication
        from django.contrib.auth.models import AnonymousUser
        if request.user.is_authenticated:
            return
        try:
            user = AnonymousUser()
            result = MultiTokenAuthentication().authenticate(request)
            if result:
                user, token = result
            request.user = user
        except exceptions.AuthenticationFailed:
            pass


class DRFTokenSocketMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send, *args, **kwargs):
        from authentication.authentication import WebsocketMultiTokenAuthentication
        from django.contrib.auth.models import AnonymousUser
        scope = dict(scope)
        try:
            user = AnonymousUser()
            result = await WebsocketMultiTokenAuthentication().authenticate_websocket(scope)
            if result:
                user, token = result
            scope['user'] = user
        except exceptions.AuthenticationFailed:
            scope['user'] = AnonymousUser()
        return await self.app(scope, receive, send)

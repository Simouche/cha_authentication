from importlib import import_module

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login, Permission, Group
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView, RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.forms import LoginForm
from authentication.models import MultiToken, Verification
from authentication.permissions import IsReadOnly
from authentication.serializers import AdvancedAuthTokenSerializer, PasswordResetSerializer, \
    RequestPasswordResetSerializer, PermissionSerializer, GroupSerializer


class SessionLogin(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login.html")

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect("/")
        return render(request, "login.html")


class LoginAPIView(ObtainAuthToken):
    serializer_class = AdvancedAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        context = dict(request=request, view=self)
        serializer = self.serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        self.run_custom_validation(user)
        update_last_login(None, user, )
        token = MultiToken.objects.create(user=user)
        data = {'token': token.key}
        data.update(
            model_to_dict(
                user,
                fields=('email', 'phone', 'id', 'selected_language',)
            )
        )
        data['groups'] = [group.name for group in user.groups.all()]

        return Response(data)

    def run_custom_validation(self, user):
        if hasattr(settings, 'MORE_USER_VALIDATION') and settings.MORE_USER_VALIDATION != 'NONE':
            module_name, func_name = settings.MORE_USER_VALIDATION.rsplit('.', 1)
            module = import_module(module_name)
            custom_validation = getattr(module, func_name)
            custom_validation(user)


class CheckAuth(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        data = {"groups": [group.name for group in request.user.groups.all()]}
        return Response({"connected": True, **data})


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.request.auth.delete()
        return Response(status=204)


class ResetPasswordApiView(GenericAPIView):
    http_method_names = ['post', 'get']
    serializer_class = PasswordResetSerializer

    def get(self, request, *args, **kwargs):
        if request.query_params.get('otp'):
            if Verification.objects.filter(otp=request.query_params.get('otp'), expired=False).exists():
                return Response({"valid": True})
        return Response({"valid": False})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"details": _("Password reset successfully")}
        return Response(response)


class RequestPasswordResetApiView(CreateAPIView):
    serializer_class = RequestPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"details": _("Password reset requested.")}
        return Response(response)


class PermissionView(ListAPIView, RetrieveAPIView):
    queryset = Permission.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = PermissionSerializer


class GroupView(ListAPIView, RetrieveAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, IsReadOnly]
    serializer_class = GroupSerializer

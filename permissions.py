from typing import Iterable

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsReadOnly(BasePermission):
    """
    The request is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)


class IsStaff(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class Or(BasePermission):

    def __init__(self, perms: Iterable['BasePermission']):
        self.perms = perms
        super().__init__()

    def has_permission(self, request, view):
        for perm in self.perms:
            if perm.has_permission(request, view):
                return True
        return False

    def __call__(self, *args, **kwargs):
        return self


class And(BasePermission):
    def __init__(self, perms: Iterable['BasePermission']):
        self.perms = perms

    def has_permission(self, request, view):
        for perm in self.perms:
            if not perm.has_permission(request, view):
                return False
        return True



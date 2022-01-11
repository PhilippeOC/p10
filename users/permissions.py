from rest_framework import permissions
from rest_framework.exceptions import ValidationError


class SignupPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.is_superuser:
                return True

        if not request.user.is_superuser:
            raise ValidationError("Seul un administrateur peut inscrire un nouvel utilisateur.")
        return True

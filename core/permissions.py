from rest_framework.permissions import BasePermission

from .models import Usuario


class HasAnyRole(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsAdminOrManager(HasAnyRole):
    allowed_roles = (Usuario.Roles.ADMIN, Usuario.Roles.GERENTE)


class IsStaffOperacao(HasAnyRole):
    allowed_roles = (
        Usuario.Roles.ADMIN,
        Usuario.Roles.GERENTE,
        Usuario.Roles.ATENDENTE,
    )


class IsCozinhaOuGestao(HasAnyRole):
    allowed_roles = (
        Usuario.Roles.ADMIN,
        Usuario.Roles.GERENTE,
        Usuario.Roles.COZINHA,
    )

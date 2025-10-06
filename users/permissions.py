from rest_framework.permissions import BasePermission

class IsSalonAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == request.user.Roles.ADMIN and
            request.user.is_approved
        )

class IsStylist(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == request.user.Roles.STYLIST and
            request.user.is_approved
        )

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == request.user.Roles.CUSTOMER and
            request.user.is_active
        )

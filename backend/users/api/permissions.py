from rest_framework.permissions import BasePermission

class IsDivisionalOffice(BasePermission):
    def has_permission(self, request, view):

        return bool(request.user and request.user.is_divisional)

class IsSubDivisionalOffice(BasePermission):
    def has_permission(self, request, view):

        return bool(request.user and request.user.is_sub_divisional)
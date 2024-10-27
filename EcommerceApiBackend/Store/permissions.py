from rest_framework import permissions


class IsAdminOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow admin or staff users to create .
    """

    def has_permission(self, request, view):
        # SAFE_METHODS are GET, HEAD, and OPTIONS.
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow any user to read data

        # Check if the user is authenticated and is admin or staff
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    
class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow seller to create product.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow any user to read data
        return request.user and request.user.is_authenticated and request.user.is_seller
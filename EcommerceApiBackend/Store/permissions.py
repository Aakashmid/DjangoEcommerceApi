from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Order 
from django.utils.translation import gettext_lazy as _

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
    

class IsOrderItemByBuyerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow order items created by the buyer or admin to be viewed or updated.
    """
    def has_permission(self, request, view):
        order_id = view.kwargs.get("order_id")
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            return order.buyer == request.user or request.user.is_staff
        else:
            return False
    
    def has_object_permission(self, request, view, obj):
        '''object(model) level permission '''
        return obj.order.buyer == request.user or request.user.is_staff
    
class IsOrderByBuyerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow order created by the buyer or admin to be viewed or updated.
    """
    def has_permission(self, request, view):
        order_id = view.kwargs.get("order_id",None)
        if order_id is not None:
            order = get_object_or_404(Order, id=order_id)
            return order.buyer == request.user or request.user.is_staff
        else:
            return request.user.is_authenticated

class IsOrderItemPending(permissions.BasePermission):
    """
    Check the status of order is pending or completed before creating, updating and deleting order items
    """
    def has_permission(self, request, view):
        order_id = view.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        if view.action in ("list",):
            return True
        return order.status == "P"
    
    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        return obj.order.status == "P"



class IsOrderPending(permissions.BasePermission):
    """
    Check the status of order is pending or completed before updating/deleting instance
    """
    message = _("Updating or deleting closed order is not allowed.")
    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        return obj.status == "P"

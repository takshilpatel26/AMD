"""
Custom Permissions - Reusable permission classes for API views
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsFarmerOrAbove(permissions.BasePermission):
    """
    Permission for farmer role and above (Farmer, Sarpanch, Utility, Government)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsSarpanchOrAbove(permissions.BasePermission):
    """
    Permission for Sarpanch role and above (Sarpanch, Utility, Government)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['sarpanch', 'utility', 'government']


class IsUtilityOrAbove(permissions.BasePermission):
    """
    Permission for Utility role and above (Utility, Government)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['utility', 'government']


class IsGovernment(permissions.BasePermission):
    """
    Permission for Government role only
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'government'


class IsOwnerOrStaffReadOnly(permissions.BasePermission):
    """
    Owners can edit, staff can read
    """
    def has_object_permission(self, request, view, obj):
        # Staff can read
        if request.user.is_staff and request.method in permissions.SAFE_METHODS:
            return True
        
        # Owner can do anything
        return obj.user == request.user

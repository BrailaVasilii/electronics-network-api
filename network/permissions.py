from rest_framework import permissions


class IsActiveStaff(permissions.BasePermission):
    """
    Custom permission to only allow active staff users to access the API.
    
    Requires:
    - User must be authenticated
    - User must be active
    - User must be staff
    """
    
    def has_permission(self, request, view):
        """
        Check if user has permission to access the view
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is active
        if not request.user.is_active:
            return False
        
        # Check if user is staff
        if not request.user.is_staff:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access a specific object
        Same requirements as has_permission
        """
        return self.has_permission(request, view)
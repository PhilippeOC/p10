from rest_framework import permissions

from .models import Contributor

class IsOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        author = Contributor.objects.get(project_id=obj.id).user_id
        if request.method in permissions.SAFE_METHODS:
            return True if author == request.user.id else False 
        return author == request.user.id
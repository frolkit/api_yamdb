from rest_framework import permissions

class IsModeratorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'moderator'
from rest_framework.permissions import BasePermission


class IsCommentOwnerOrProjectCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Comment owner can edit/delete
        if obj.user == request.user:
            return True

        # Project creator can delete comments on their project
        if obj.project.created_by == request.user:
            return True

        return False



class HasProfileForUnsafeMethods(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        user = request.user
        return user.is_authenticated and hasattr(user, 'scientist_profile')
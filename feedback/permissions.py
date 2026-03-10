from rest_framework.permissions import BasePermission


class IsCommentOwnerOrProjectCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS are always allowed
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Comment owner can edit/delete
        if obj.user == request.user:
            return True

        # Project creator can delete comments on their project
        if obj.project.created_by == request.user:
            return True

        return False
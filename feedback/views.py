from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from projects.models import Project
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsCommentOwnerOrProjectCreator


class ProjectCommentListCreateAPI(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)

        comments = Comment.objects.filter(
            project=project,
            parent__isnull=True
        )

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                project=project
            )
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)



class CommentDetailAPI(APIView):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsCommentOwnerOrProjectCreator
    ]

    def put(self, request, slug, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        self.check_object_permissions(request, comment)

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, slug, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        self.check_object_permissions(request, comment)

        comment.delete()
        return Response(status=204)
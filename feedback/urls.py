from django.urls import path
from .views import ProjectCommentListCreateAPI, CommentDetailAPI

urlpatterns = [
    path(
        "projects/<slug:slug>/comments/",
        ProjectCommentListCreateAPI.as_view(),
        name="project-comments-api"
    ),
    path(
        "projects/<slug:slug>/comments/<int:comment_id>/",
        CommentDetailAPI.as_view(),
        name="comment-detail"
    ),
]
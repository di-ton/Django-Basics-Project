from django.core.exceptions import ValidationError
from django.test import TestCase
from feedback.models import Comment
from accounts.models import User
from feedback.permissions import IsCommentOwnerOrProjectCreator
from feedback.serializers import CommentSerializer
from projects.choices import CategoryChoices
from projects.models import Project


class CommentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@gmail.com",
            password="pass12345"
        )

        self.project = Project.objects.create(
            title="Test Project",
            slug="test-project",
            created_by=self.user,
            keywords="science, ai, biology",
            description="Test project description",
            funder="EU",
            project_number="PRJ-001",
            category=CategoryChoices.BIO
        )

    def test_create_comment(self):
        comment = Comment.objects.create(
            project=self.project,
            user=self.user,
            content="Great project!"
        )

        self.assertEqual(comment.content, "Great project!")
        self.assertEqual(comment.user, self.user)



class CommentValidationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user2@gmail.com",
            password="pass12345pass"
        )

        self.project = Project.objects.create(
            title="Test Project",
            slug="test-project",
            created_by=self.user,
            keywords="science, ai, biology",
            description="Test project description",
            funder="EU",
            project_number="PRJ-001",
            category=CategoryChoices.BIO
        )

    def test_only_one_level_reply_allowed(self):

        parent = Comment.objects.create(
            project=self.project,
            user=self.user,
            content="Main comment"
        )

        reply = Comment.objects.create(
            project=self.project,
            user=self.user,
            content="Reply",
            parent=parent
        )

        nested_reply = Comment(
            project=self.project,
            user=self.user,
            content="Nested reply",
            parent=reply
        )

        with self.assertRaises(ValidationError):
            nested_reply.clean()

class CommentSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user3@gmail.com",
            password="pass12345"
        )

        self.project = Project.objects.create(
            title="Test Project",
            slug="test-project",
            created_by=self.user,
            keywords="science, ai, biology",
            description="Test project description",
            funder="EU",
            project_number="PRJ-001",
            category=CategoryChoices.MED
        )

    def test_serializer_returns_replies(self):

        parent = Comment.objects.create(
            project=self.project,
            user=self.user,
            content="Main comment"
        )

        Comment.objects.create(
            project=self.project,
            user=self.user,
            content="Reply comment",
            parent=parent
        )

        serializer = CommentSerializer(parent)

        self.assertEqual(len(serializer.data["replies"]), 1)



class CommentPermissionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user4@gmail.com",
            password="pass12345pass"
        )

        self.project = Project.objects.create(
            title="Test Project",
            slug="test-project",
            created_by=self.user,
            keywords="science, ai, biology",
            description="Test project description",
            funder="EU",
            project_number="PRJ-001",
            category=CategoryChoices.MATH
        )

    def test_comment_owner_has_permission(self):

        comment = Comment.objects.create(
            project=self.project,
            user=self.user,
            content="My comment"
        )

        permission = IsCommentOwnerOrProjectCreator()

        request = type("Request", (), {
            "method": "PUT",
            "user": self.user
        })

        self.assertTrue(
            permission.has_object_permission(request, None, comment)
        )



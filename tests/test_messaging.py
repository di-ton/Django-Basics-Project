import uuid

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.choices import AcademicDegreeChoices
from accounts.models import ScientistProfile, User
from messaging.models import MessageRecipient, Message
from projects.choices import CategoryChoices
from projects.models import Project


def create_user_with_profile(email, password):
    user = User.objects.create_user(email=email, password=password)

    ScientistProfile.objects.create(
        user=user,
        first_name="Test",
        last_name="User",
        academic_degree=AcademicDegreeChoices.PHD,
        affiliation="Test University",
        orcid_id=str(uuid.uuid4())[:19]
    )

    return user

def create_required_groups():
    Group.objects.get_or_create(name="Profile Moderators")
    Group.objects.get_or_create(name="Content Moderators")


class SendMessageTests(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name="Profile Moderators")
        Group.objects.get_or_create(name="Content Moderators")

        self.sender = create_user_with_profile("sender@gmail.com", "pass12345pass")
        self.recipient_user = create_user_with_profile("recipient@gmail.com", "pass123456")
        self.recipient_profile = self.recipient_user.scientist_profile

        self.group = Group.objects.get(name="Content Moderators")

    def test_send_message_creates_recipients(self):
        self.client.login(email="sender@gmail.com", password="pass12345pass")

        self.client.post(reverse("send-message", args=[self.recipient_profile.slug]), {
            "subject": "Hello",
            "body": "Test message"
        })

        self.assertEqual(MessageRecipient.objects.count(), 2)


class InboxTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="Profile Moderators")
        Group.objects.get_or_create(name="Content Moderators")

    def test_inbox_excludes_own_messages(self):
        user = create_user_with_profile("user@gmail.com", "pass12345pass")
        message = Message.objects.create(sender=user, subject="Article", body="Let's submitted it today.")
        MessageRecipient.objects.create(message=message, recipient=user)
        self.client.login(email="user@gmail.com", password="pass12345pass")
        response = self.client.get(reverse("inbox"))

        self.assertEqual(len(response.context["messages"]), 0)


class MessageDetailTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="Profile Moderators")
        Group.objects.get_or_create(name="Content Moderators")

    def test_message_marked_as_read(self):
        sender = create_user_with_profile("send@abv.bg", "pass12345pass")
        recipient = create_user_with_profile("recip@gmail.com", "pass123456")
        message = Message.objects.create(sender=sender, subject="Add members", body="There is a researcher who wants to join the project")

        MessageRecipient.objects.create(message=message, recipient=recipient, is_read=False)

        self.client.login(email="recip@gmail.com", password="pass123456")

        self.client.get(reverse("message-detail", args=[message.pk]))

        received_message = MessageRecipient.objects.get(message=message, recipient=recipient)
        self.assertTrue(received_message.is_read)


class MessagePermissionTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="Profile Moderators")
        Group.objects.get_or_create(name="Content Moderators")

    def test_user_cannot_view_other_messages(self):
        sender = create_user_with_profile("send@abv.bg", "pass12345pass")
        recipient = create_user_with_profile("recip@gmail.com", "pass123456")
        outsider = create_user_with_profile("out@gmail.com", "pass123word")

        message = Message.objects.create(sender=sender, subject="test subject", body="Test content")
        MessageRecipient.objects.create(message=message, recipient=recipient)

        self.client.login(email="out@gmail.com", password="pass123word")

        response = self.client.get(reverse("message-detail", args=[message.pk]))

        self.assertEqual(response.status_code, 403)


class MessageModelTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="Profile Moderators")
        Group.objects.get_or_create(name="Content Moderators")

    def test_is_project_message(self):
        user = create_user_with_profile("user@gmail.com", "pass12345pass")

        message = Message.objects.create(
            sender=user,
            subject="test",
            body="TestTestTestTestTest"
        )

        self.assertFalse(message.is_project_message)


class ReportTests(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name="Profile Moderators")
        Group.objects.get_or_create(name="Content Moderators")

        self.user = create_user_with_profile("user@gmail.com", "pass12345pass")

        self.project = Project.objects.create(
            title="Test Project",
            slug="test-project",
            created_by=self.user,
            keywords="models, ai, classification",
            description="Test project description",
            funder="BNSF",
            project_number="PRJ-001",
            category=CategoryChoices.MATH
        )

        self.group = Group.objects.get(name="Content Moderators")

    def test_report_sets_is_report_true(self):
        self.client.login(email="user@gmail.com", password="pass12345pass")

        self.client.post(reverse("project-report", args=[self.project.slug]), {
            "subject": "Report",
            "body": "This is inappropriate"
        })

        message = Message.objects.first()

        self.assertTrue(message.is_report)

    def test_report_sent_to_moderators(self):
        moderator = create_user_with_profile("mod@abv.bg", "pass12345pass")

        moderator.groups.add(self.group)

        self.client.login(email="user@gmail.com", password="pass12345pass")

        self.client.post(reverse("project-report", args=[self.project.slug]), {
            "subject": "Report",
            "body": "Spam project"
        })

        self.assertEqual(
            MessageRecipient.objects.filter(recipient=moderator).count(),
            1
        )

    def test_report_creates_sender_copy(self):
        self.client.login(email="user@gmail.com", password="pass12345pass")

        self.client.post(reverse("project-report", args=[self.project.slug]), {
            "subject": "Report",
            "body": "Inappropriate content"
        })

        sender_copy = MessageRecipient.objects.get(recipient=self.user)

        self.assertTrue(sender_copy.is_read)



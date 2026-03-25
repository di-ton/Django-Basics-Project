from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.urls import reverse

from accounts.models import User, ScientistProfile
from accounts.choices import AcademicDegreeChoices
from projects.models import Project, ProjectMembership, ScientificOrganization
from projects.choices import CategoryChoices


class ProjectModelTests(TestCase):

    def setUp(self):
        Group.objects.create(name="Profile Moderators")

        self.user = User.objects.create_user(
            email="user@gmail.com",
            password="pass12345pass"
        )

        self.profile = ScientistProfile.objects.create(
            user=self.user,
            first_name="Ivan",
            last_name="Petrov",
            academic_degree=AcademicDegreeChoices.PHD,
            affiliation="SU",
            orcid_id="0000-0000-0000-0001"
        )

    def create_project(self):
        return Project.objects.create(
            title="Test Project",
            keywords="models, machine learning, data",
            description="Test description",
            funder="BNSF",
            project_number="FNI-001",
            category=CategoryChoices.MATH,
            created_by=self.user
        )

    def test_project_creation(self):
        project = self.create_project()
        self.assertEqual(project.title, "Test Project")

    def test_project_slug_generated(self):
        project = self.create_project()
        self.assertIsNotNone(project.slug)

    def test_project_str(self):
        project = self.create_project()
        self.assertEqual(str(project), "Test Project")

    def test_project_is_editable_true(self):
        project = self.create_project()
        self.assertTrue(project.is_editable())

    def test_project_is_editable_false_when_locked(self):
        project = self.create_project()
        project.is_locked = True
        self.assertFalse(project.is_editable())


class ProjectValidationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@gmail.com",
            password="pass12345pass"
        )

    def test_keywords_validation_without_acronym(self):
        project = Project(
            title="Test",
            keywords="machine learning",  #  less than 3
            description="Description",
            funder="BNSF",
            project_number="FNI-2",
            category=CategoryChoices.MATH,
            created_by=self.user
        )

        with self.assertRaises(ValidationError):
            project.clean()

    def test_keywords_valid(self):
        project = Project(
            title="Test",
            keywords="ai, ml, data",
            description="Description",
            funder="BNSF",
            project_number="FNI-2",
            category=CategoryChoices.MATH,
            created_by=self.user
        )

        project.clean()

    def test_acronym_skips_keyword_validation(self):
        project = Project(
            title="Test",
            acronym="TestAI",
            keywords="machine learning",
            description="Description",
            funder="BNSF",
            project_number="FNI-2",
            category=CategoryChoices.MATH,
            created_by=self.user
        )

        project.clean()



class ProjectMembershipTests(TestCase):

    def setUp(self):
        Group.objects.create(name="Profile Moderators")

        self.user = User.objects.create_user(
            email="user@gmail.com",
            password="pass12345pass"
        )

        self.profile = ScientistProfile.objects.create(
            user=self.user,
            first_name="Ivan",
            last_name="Petrov",
            academic_degree=AcademicDegreeChoices.PHD,
            affiliation="MU-Sofia",
            orcid_id="0000-0000-0000-0002"
        )

        self.project = Project.objects.create(
            title="Test Project",
            keywords="models, machine learning, data",
            description="Test description",
            funder="BNSF",
            project_number="FNI-001",
            category=CategoryChoices.MATH,
            created_by=self.user
        )

    def test_create_membership(self):
        membership = ProjectMembership.objects.create(
            project=self.project,
            scientist=self.profile,
            name="Ivan Petrov",
            email="user@gmail.com",
            role="leader"
        )

        self.assertEqual(membership.role, "leader")

    def test_only_one_leader_constraint(self):
        ProjectMembership.objects.create(
            project=self.project,
            scientist=self.profile,
            name="Ivan",
            email="user@gmail.com",
            role="leader"
        )

        with self.assertRaises(Exception):
            ProjectMembership.objects.create(
                project=self.project,
                name="Other",
                role="leader"
            )

    def test_can_manage_project_creator(self):
        self.assertTrue(self.project.can_manage(self.user))

    def test_can_manage_member(self):
        membership = ProjectMembership.objects.create(
            project=self.project,
            scientist=self.profile,
            name="Ivan",
            role="member"
        )

        self.assertTrue(self.project.can_manage(self.user))

    def test_cannot_manage_other_user(self):
        other = User.objects.create_user(
            email="other@abv.bg",
            password="pass1234pass"
        )

        self.assertFalse(self.project.can_manage(other))


class OrganizationTests(TestCase):

    def test_slug_generated(self):
        org = ScientificOrganization.objects.create(
            name="Bulgarian Academy of Sciences",
            country="BG"
        )

        self.assertIsNotNone(org.slug)

    def test_website_auto_prefix(self):
        org = ScientificOrganization.objects.create(
            name="Bulgarian Academy of Sciences",
            country="BG",
            website="bas.bg"
        )

        self.assertTrue(org.website.startswith("https://"))


class ProjectViewTests(TestCase):

    def setUp(self):
        Group.objects.create(name="Profile Moderators")

        self.user = User.objects.create_user(
            email="user@gmail.com",
            password="pass1234pass"
        )

        self.profile = ScientistProfile.objects.create(
            user=self.user,
            first_name="Ivan",
            last_name="Petrov",
            academic_degree=AcademicDegreeChoices.PHD,
            affiliation="MU-Sofia",
            orcid_id="0000-0000-0000-0003"
        )

        self.project = Project.objects.create(
            title="Test Project",
            keywords="machine learning, data, models",
            description="Test",
            funder="BNSF",
            project_number="FNI-001-12",
            category=CategoryChoices.MATH,
            created_by=self.user
        )

    def test_lock_project(self):
        moderator = User.objects.create_user(
            email="mod@gmail.com",
            password="pass1234pass"
        )

        group = Group.objects.create(name="Content Moderators")
        moderator.groups.add(group)

        self.client.login(email="mod@gmail.com", password="pass1234pass")

        self.client.get(reverse("project-lock", args=[self.project.slug]))

        self.project.refresh_from_db()
        self.assertTrue(self.project.is_locked)


    def test_unlock_project(self):
        moderator = User.objects.create_user(
            email="mod@gmail.com",
            password="pass1234pass"
        )

        group = Group.objects.create(name="Content Moderators")
        moderator.groups.add(group)

        self.project.is_locked = True
        self.project.save()

        self.client.login(email="mod@gmail.com", password="pass1234pass")

        self.client.get(reverse("project-unlock", args=[self.project.slug]))

        self.project.refresh_from_db()
        self.assertFalse(self.project.is_locked)


    def test_disable_project_sets_fields(self):
        moderator = User.objects.create_user(
            email="mod@gmail.com",
            password="pass1234pass"
        )

        group = Group.objects.create(name="Content Moderators")
        moderator.groups.add(group)

        self.client.login(email="mod@gmail.com", password="pass1234pass")

        self.client.post(reverse("project-disable", args=[self.project.slug]), {
            "moderation_note": "Plagiarism"
        })

        self.project.refresh_from_db()

        self.assertTrue(self.project.is_disabled)
        self.assertEqual(self.project.disabled_by, moderator)
        self.assertEqual(self.project.moderation_note, "Plagiarism")


    def test_disabled_project_not_visible(self):
        self.project.is_disabled = True
        self.project.save()

        self.client.login(email="user@gmail.com", password="pass12345pass")

        response = self.client.get(reverse("project-overview", args=[self.project.slug]))

        self.assertEqual(response.status_code, 404)


from django.test import TestCase
from django.contrib.auth.models import Group
from accounts.choices import AcademicDegreeChoices
from accounts.models import User, ScientistProfile
from django.core.exceptions import ValidationError
from accounts.validators import OrcidIdValidator, ScopusIDValidator
from django.contrib.auth.models import Permission
from django.urls import reverse


class UserModelTests(TestCase):

    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="test@abv.bg",
            password="test1234pass"
        )

        self.assertEqual(user.email, "test@abv.bg")
        self.assertTrue(user.check_password("test1234pass"))


class ScientistProfileTests(TestCase):

    def test_full_name_property(self):

        Group.objects.create(name="Profile Moderators")

        user = User.objects.create_user(
            email="test2@abv.bg",
            password="test1234pass"
        )

        profile = ScientistProfile.objects.create(
            user=user,
            first_name="Georgi",
            last_name="Petrov",
            academic_degree=AcademicDegreeChoices.PHD,
            affiliation="Sofia University",
            orcid_id="0000-0000-0000-0068"
        )

        self.assertEqual(profile.full_name, "Georgi Petrov")


class ValidatorTests(TestCase):

    def test_invalid_orcid(self):
        validator = OrcidIdValidator()

        with self.assertRaises(ValidationError):
            validator("invalid-orcid")



class RegisterViewTests(TestCase):

    def test_register_view_creates_user(self):
        response = self.client.post(reverse("register"), {
            "email": "testuser@gmail.com",
            "password1": "pass123pass!",
            "password2": "pass123pass!"
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="testuser@gmail.com").exists())



class BanProfileTests(TestCase):

    def test_ban_profile_deactivates_user(self):
        Group.objects.create(name="Profile Moderators")

        moderator = User.objects.create_user(
            email="mod@gmail.com",
            password="pass1234pass"
        )

        permission = Permission.objects.get(codename="can_ban_profile")
        moderator.user_permissions.add(permission)

        user = User.objects.create_user(
            email="user@abv.bg",
            password="pass123pass"
        )

        profile = ScientistProfile.objects.create(
            user=user,
            first_name="Ivan",
            last_name="Petrov",
            academic_degree=AcademicDegreeChoices.PHD,
            affiliation="Sofia University",
            orcid_id="0000-0033-0000-0033"
        )

        self.client.login(email="mod@gmail.com", password="pass1234pass")

        self.client.post(reverse("profile-ban", args=[profile.slug]))

        user.refresh_from_db()
        self.assertFalse(user.is_active)


class ScientistProfileEligibilityTests(TestCase):

    def setUp(self):
        Group.objects.create(name="Profile Moderators")

    def test_profile_is_eligible(self):
        user = User.objects.create_user(
            email="testuser1@gmail.com",
            password="pass12345"
        )

        profile = ScientistProfile.objects.create(
            user=user,
            first_name="Ivan",
            last_name="Ivanov",
            academic_degree=AcademicDegreeChoices.PHD,
            affiliation="Sofia University",
            orcid_id="0000-0000-0000-1111",
            is_approved=True
        )

        self.assertTrue(profile.is_eligible)


class OrcidValidatorTests(TestCase):

    def test_invalid_orcid_format(self):
        validator = OrcidIdValidator()

        with self.assertRaises(ValidationError):
            validator("123456")


class ScopusValidatorTests(TestCase):

    def test_scopus_id_must_be_digits(self):
        validator = ScopusIDValidator()

        with self.assertRaises(ValidationError):
            validator("1234abcd")




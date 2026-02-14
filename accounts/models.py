from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from accounts.choices import AcademicDegreeChoices, AcademicPositionChoices
from accounts.managers import UserManager
from accounts.validators import OrcidIdValidator, ScopusIDValidator
from common.models import TimeStampedModel
from projects.models import Project, ProjectMembership


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"

    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)   # for exam
    is_staff = models.BooleanField(default=False)

    objects = UserManager()


class ScientistProfile(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="scientist_profile"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    academic_degree = models.CharField(
            max_length=20,
            choices=AcademicDegreeChoices.choices,
        )
    academic_position = models.CharField(
        max_length=30,
        choices=AcademicPositionChoices.choices,
        blank=True,
        null=True,
    )
    affiliation = models.CharField(max_length=200)
    orcid_id = models.CharField(
        max_length=19,
        validators=[OrcidIdValidator],
        unique=True,
        null=True,
        blank=True,
    )
    scopus_id = models.CharField(
        max_length=20,
        validators=[ScopusIDValidator],
        unique=True,
        null=True,
        blank=True,
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )

    profile_picture_url = models.URLField(
        blank=True,
        null=True,
        help_text="Paste a link to your profile picture (optional)",
    )
    research_interests = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True) # for exam

    slug = models.SlugField(max_length=200, unique=True, blank=True, editable=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_eligible(self):
        return self.user.is_active and self.is_approved

    @property
    def all_projects(self):
        return Project.objects.filter(
            memberships__scientist=self
        ).distinct()

    @property
    def project_count(self):
        return self.all_projects.count()

    def __str__(self):
        return self.full_name

    def clean(self):
        super().clean()

        DEGREE_RANK = {
            "PHD_STUDENT": 1,
            "PHD": 2,
            "DSC": 3,
        }

        PHD_REQUIRED_POSITIONS = {
            AcademicPositionChoices.POSTDOC,
            AcademicPositionChoices.ASSISTANT_PROF,
            AcademicPositionChoices.ASSOCIATE_PROF,
            AcademicPositionChoices.PROFESSOR,
        }


        if ScientistProfile.objects.filter(pk=self.pk).exists():
            old = ScientistProfile.objects.get(pk=self.pk)
            if DEGREE_RANK[self.academic_degree] < DEGREE_RANK[old.academic_degree]:
                raise ValidationError("Academic degree cannot be downgraded.")

        if (
                self.academic_position in PHD_REQUIRED_POSITIONS
                and self.academic_degree == AcademicDegreeChoices.PHD_STUDENT
        ):
            raise ValidationError({
                "academic_position": "This academic position requires a completed PhD degree.",
                "academic_degree": "PhD Student is not compatible with this position.",
            })

        if not self.orcid_id and not self.scopus_id:
            raise ValidationError({
                "orcid_id": "Either ORCID or Scopus ID is required.",
                "scopus_id": "Either ORCID or Scopus ID is required.",
            })

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        self.full_clean()
        super().save(*args, **kwargs)

        if is_new and not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}-{self.user.pk}")
            super().save(update_fields=["slug"])

        if is_new and self.user.email:
            ProjectMembership.objects.filter(
                scientist__isnull=True,
                email__iexact=self.user.email
            ).update(scientist=self)


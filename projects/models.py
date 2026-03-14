from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from common.models import TimeStampedModel
from projects.choices import ProjectStatusChoices, JournalQuartileChoices, CategoryChoices, ParticipationTypeChoices


class ScientificOrganization(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    # is_base_organization = models.BooleanField(default=False, verbose_name="Base organization")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.website and not self.website.startswith(("http://", "https://")):
            self.website = "https://" + self.website

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class Project(TimeStampedModel):
    title = models.CharField(max_length=255)
    acronym = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    keywords = models.CharField(
        max_length=255,
        help_text="Enter at least 3 keywords, separated by commas"
    )
    description = models.TextField()
    funder = models.CharField(max_length=255)
    project_number = models.CharField(max_length=50)
    start_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=ProjectStatusChoices.choices,
        default=ProjectStatusChoices.ONGOING
    )

    category = models.CharField(
        max_length=10,
        choices=CategoryChoices.choices
    )
    organizations = models.ManyToManyField(
        ScientificOrganization,
        related_name="projects",
        through="ProjectOrganization",
        blank=True
    )


    slug = models.SlugField(
        unique=True,
        max_length=120,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_projects"
    )


    def can_manage(self, user):
        if not user.is_authenticated:
            return False

        if user == self.created_by:
            return True

        return self.memberships.filter(
            Q(role="leader") | Q(role="member"),
            scientist__user=user
        ).exists()


    def clean(self):
        if not self.acronym:
            keywords = [k.strip() for k in self.keywords.split(",") if k.strip()]
            if len(keywords) < 3:
                raise ValidationError({
                    "keywords": "Please enter at least 3 keywords if no acronym is provided."
                })

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        self.full_clean()
        super().save(*args, **kwargs)

        if is_new and not self.slug:
            if self.acronym:
                base = slugify(self.acronym)
            else:
                keywords = [k.strip() for k in self.keywords.split(",") if k.strip()]
                base = slugify("-".join(keywords[:3]))

            self.slug = f"{base}-{self.pk}"
            super().save(update_fields=["slug"])

    # def get_absolute_url(self):
    #     return reverse("project-overview", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ProjectOrganization(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_organizations"
    )

    organization = models.ForeignKey(
        ScientificOrganization,
        on_delete=models.CASCADE,
        related_name="project_links"
    )

    is_base_organization = models.BooleanField(
        default=False,
        verbose_name="Base organization"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "organization"],
                name="unique_project_organization"
            ),
            models.UniqueConstraint(
                fields=["project"],
                condition=Q(is_base_organization=True),
                name="one_base_organization_per_project"
            )
        ]

    def __str__(self):
        return f"{self.organization} - {self.project}"



class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ("leader", "Leader"),
        ("member", "Member"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)

    scientist = models.ForeignKey(
        "accounts.ScientistProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="project_memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )



    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project"],
                condition=models.Q(role="leader"),
                name="one_leader_per_project",
            )
        ]




class Article(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="articles"
    )

    title = models.CharField(max_length=500)
    authors = models.TextField(
        blank=True,
        help_text="List of authors as they appear in the publication"
    )
    journal = models.CharField(max_length=255, blank=True)
    journal_quartile = models.CharField(
        max_length=2,
        choices=JournalQuartileChoices.choices,
        default=JournalQuartileChoices.NA
    )

    publication_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Year of publication"
    )

    doi = models.CharField(
        max_length=100,
        blank=True,
        help_text="Digital Object Identifier"
    )

    article_url = models.URLField(
        blank=True,
        help_text="Link to the article"
    )

    def __str__(self):
        return self.title


class ScientificEvent(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="events"
    )

    name = models.CharField(max_length=255)

    location = models.CharField(max_length=255, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    event_url = models.URLField(
        blank=True,
        help_text="Scientific forum website"
    )

    def __str__(self):
        return self.name


class EventParticipation(models.Model):
    event = models.ForeignKey(
        ScientificEvent,
        on_delete=models.CASCADE,
        related_name="participations"
    )

    title = models.CharField(max_length=255)

    authors = models.TextField(
        blank=True,
        help_text="Authors as listed in the presentation/poster"
    )


    participation_type = models.CharField(
        max_length=20,
        choices=ParticipationTypeChoices.choices,
        blank=True
    )

    def __str__(self):
        return self.title

























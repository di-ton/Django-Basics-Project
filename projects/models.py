from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from common.models import TimeStampedModel
from projects.choices import ProjectStatusChoices, JournalQuartileChoices


class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ScientificOrganization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    is_base_organization = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
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

    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.PROTECT,
        related_name="projects"
    )
    organizations = models.ManyToManyField(
        ScientificOrganization,
        related_name="projects",
        blank=True
    )

    leader = models.ForeignKey(
        "accounts.ScientistProfile",
        on_delete=models.PROTECT,
        related_name="led_projects"
    )

    members = models.ManyToManyField(
        "accounts.ScientistProfile",
        related_name="member_projects",
        blank=True
    )


    slug = models.SlugField(
        unique=True,
        max_length=120,
        blank=True
    )

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

    def __str__(self):
        return self.title


class Article(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="articles"
    )

    title = models.CharField(max_length=500)
    authors = models.ManyToManyField("accounts.ScientistProfile", related_name="articles")
    journal = models.CharField(max_length=255, blank=True)
    journal_quartile = models.CharField(
        max_length=2,
        choices=JournalQuartileChoices.choices,
        default=JournalQuartileChoices.NA
    )
    publication_date = models.DateField(null=True, blank=True)

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




























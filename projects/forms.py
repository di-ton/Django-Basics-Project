from django import forms
from accounts.models import ScientistProfile
from projects.models import ScientificEvent, Project, Article, ProjectMembership, ScientificOrganization, \
    EventParticipation


class ProjectBaseForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "acronym",
            "keywords",
            "description",
            "funder",
            "project_number",
            "start_date",
            "status",
            "category",
        ]

        labels = {
            "title": "Project title",
            "acronym": "Acronym (optional)",
            "keywords": "Keywords",
            "project_number": "Project number",
            "start_date": "Start date",
        }

        help_texts = {
            "keywords": "Enter at least 3 keywords, separated by commas",
        }

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
        }


class ProjectCreateForm(ProjectBaseForm):
    pass


class ProjectUpdateForm(ProjectBaseForm):
    pass


class ProjectDeleteForm(ProjectBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.disabled = True


class ProjectMembershipForm(forms.ModelForm):
    class Meta:
        model = ProjectMembership
        fields = [
            "name",
            "email",
            "scientist",
            "role",
        ]

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        self.fields["scientist"].required = False
        self.fields["scientist"].empty_label = "— No profile selected —"

        self.fields["name"].label = "Full name"
        self.fields["email"].label = "Email"
        self.fields["scientist"].label = "Link to an existing profile (optional)"

        if self.project:
            qs = ScientistProfile.objects.exclude(
                project_memberships__project=self.project
            )

            if self.is_bound:
                submitted_id = self.data.get(self.add_prefix("scientist"))
                if submitted_id:
                    qs = qs | ScientistProfile.objects.filter(pk=submitted_id)


            self.fields["scientist"].queryset = qs.order_by("first_name")

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        email = cleaned_data.get("email")
        scientist = cleaned_data.get("scientist")

        if role == "leader" and self.project:
            if ProjectMembership.objects.filter(
                project=self.project,
                role="leader"
            ).exists():
                raise forms.ValidationError(
                    "This project already has a leader."
                )

        if email and not scientist:
            profile = ScientistProfile.objects.filter(
                user__email__iexact=email
            ).first()
            if profile:
                cleaned_data["scientist"] = profile

        return cleaned_data



class ScientificOrganizationForm(forms.ModelForm):
    class Meta:
        model = ScientificOrganization
        fields = ["name", "country", "address", "website", "is_base_organization"]



class ArticleBaseForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "authors",
            "journal",
            "journal_quartile",
            "publication_year",
            "doi",
            "article_url",
        ]

        labels = {
            "journal_quartile": "Journal quartile (WoS or SCImago)",
            "publication_year": "Publication year",
        }

        help_texts = {
            "article_url": "Full text or publisher URL",
        }

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Article title"
            }),
            "authors": forms.Textarea(attrs={
                "rows": 2,
            }),
            "journal": forms.TextInput(attrs={
                "placeholder": "Journal name"
            }),
            "publication_year": forms.NumberInput(attrs={
                "placeholder": "e.g. 2023",
                "min": 1800,
                "max": 2100,
            }),
            "doi": forms.TextInput(attrs={
                "placeholder": "https://doi.org/..."
            }),
            "article_url": forms.URLInput(attrs={
                "placeholder": "https://..."
            }),
        }


class ArticleCreateForm(ArticleBaseForm):
    pass


class ArticleUpdateForm(ArticleBaseForm):
    pass


class ScientificEventBaseForm(forms.ModelForm):
    class Meta:
        model = ScientificEvent
        exclude = ["project"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")

        if start and end and end < start:
            raise forms.ValidationError(
                "End date cannot be earlier than start date."
            )
        return cleaned


class ScientificEventCreateForm(ScientificEventBaseForm):
    pass


class ScientificEventUpdateForm(ScientificEventBaseForm):
    pass


class EventParticipationForm(forms.ModelForm):
    class Meta:
        model = EventParticipation
        exclude = ["event"]

        labels = {
            "participation_type": "Type of participation",
        }

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Presentation / poster title"
            }),
            "authors": forms.Textarea(attrs={
                "rows": 2,
            }),
            "participation_type": forms.Select(),
        }


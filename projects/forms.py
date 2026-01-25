from django import forms

from accounts.models import ScientistProfile
from projects.models import ScientificEvent, Project, Article, ProjectMembership, ScientificOrganization


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

        # Scientist is optional
        self.fields["scientist"].required = False
        self.fields["scientist"].empty_label = "— No profile selected —"

        # Clear, neutral labels
        self.fields["name"].label = "Full name"
        self.fields["email"].label = "Email"
        self.fields["scientist"].label = "Link to an existing profile (optional)"

        # Exclude scientists already linked to this project
        if self.project:
            self.fields["scientist"].queryset = (
                ScientistProfile.objects.exclude(
                    project_memberships__project=self.project
                )
            )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        # Enforce one leader per project
        if role == "leader" and self.project:
            if ProjectMembership.objects.filter(
                project=self.project,
                role="leader"
            ).exists():
                raise forms.ValidationError(
                    "This project already has a leader."
                )

        return cleaned_data

# class ProjectMembershipForm(forms.ModelForm):
#     class Meta:
#         model = ProjectMembership
#         fields = ["name", "email", "scientist", "role"]
#
#     def __init__(self, *args, **kwargs):
#         self.project = kwargs.pop("project", None)
#         super().__init__(*args, **kwargs)
#
#         self.fields["scientist"].required = False
#
#         if self.project:
#             self.fields["scientist"].queryset = (
#                 ScientistProfile.objects.exclude(
#                     project_memberships__project=self.project
#                 )
#             )
#
#     def clean(self):
#         cleaned_data = super().clean()
#         role = cleaned_data.get("role")
#
#         if role == "leader" and self.project:
#             if ProjectMembership.objects.filter(
#                 project=self.project,
#                 role="leader"
#             ).exists():
#                 raise forms.ValidationError(
#                     "This project already has a leader."
#                 )
#
#         return cleaned_data

# class ProjectOrganizationsForm(forms.ModelForm):
#     class Meta:
#         model = Project
#         fields = ["organizations"]
#         widgets = {
#             "organizations": forms.CheckboxSelectMultiple
#         }

class ScientificOrganizationForm(forms.ModelForm):
    class Meta:
        model = ScientificOrganization
        fields = ["name", "country", "address", "website", "is_base_organization"]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["is_base_organization"].label = "Base organization"



class ArticleBaseForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "authors",
            "journal",
            "journal_quartile",
            "publication_date",
            "doi",
            "article_url",
        ]

        labels = {
            "journal_quartile": "Journal quartile",
            "publication_date": "Publication date",
        }

        help_texts = {
            "article_url": "Full text or publisher URL",
        }

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Article title"
            }),
            "authors": forms.CheckboxSelectMultiple,
            "journal": forms.TextInput(attrs={
                "placeholder": "Journal name"
            }),
            "publication_date": forms.DateInput(attrs={
                "type": "date"
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
        fields = "__all__"
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


class ScientificOrganizationForm(forms.ModelForm):
    class Meta:
        model = ScientificOrganization
        fields = [
            "name",
            "country",
            "address",
            "website",
            "description",
            "is_base_organization"
        ]

    # def clean_name(self):
    #     name = self.cleaned_data["name"]
    #
    #     if ScientificOrganization.objects.filter(name__iexact=name).exists():
    #         raise forms.ValidationError(
    #             "This organization already exists. "
    #             "Please use the existing record."
    #         )
    #
    #     return name

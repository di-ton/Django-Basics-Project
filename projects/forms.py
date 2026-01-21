from django import forms

from projects.models import ScientificEvent, Project, Article


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
            "organizations",
            "leader",
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


class ProjectMembersForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["members"]
        widgets = {
            "members": forms.CheckboxSelectMultiple
        }


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


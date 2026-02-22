from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model

from accounts.choices import AcademicDegreeChoices, AcademicPositionChoices
from accounts.models import ScientistProfile

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email address:",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
            }
        ),
    )

    password1 = forms.CharField(
        label="Password:",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a strong password",
            }
        ),
        help_text=None,
    )

    password2 = forms.CharField(
        label="Confirm password:",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Repeat your password",
            }
        ),
        help_text=None,
    )
    class Meta:
        model = User
        fields = ("email",)


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email address:",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        label="Password:",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
            }
        )
    )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email address:",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("email",)


class ScientistProfileForm(forms.ModelForm):
    class Meta:
        model = ScientistProfile
        fields = (
            "first_name",
            "last_name",
            "academic_degree",
            "academic_position",
            "affiliation",
            "orcid_id",
            "scopus_id",
            "research_interests",
            "profile_picture",
            "profile_picture_url",
        )

    first_name = forms.CharField(
        label="First name:",
        widget=forms.TextInput(attrs={"class": "form-control","placeholder": "Enter your first name"}),
    )

    last_name = forms.CharField(
        label="Last name:",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your last name"}),
    )

    academic_degree = forms.ChoiceField(
        label="Academic degree:",
        choices=list(AcademicDegreeChoices.choices),
        initial=AcademicDegreeChoices.PHD,
        widget=forms.Select(attrs={"class": "form-control","placeholder": "Enter your academic degree"}),
    )

    academic_position = forms.ChoiceField(
        required=False,
        label="Academic position:",
        choices=list(AcademicPositionChoices.choices),
        initial=AcademicPositionChoices.NONE,
        widget=forms.Select(attrs={"class": "form-control", "placeholder": "Enter your academic position"}),
    )

    affiliation = forms.CharField(
        label="Affiliation:",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your affiliation"}),
    )

    orcid_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your ORCID ID"}),
        label="ORCID ID:",
    )

    scopus_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your Scopus Author ID"}),
        label="Scopus Author ID:",
    )


    research_interests = forms.CharField(
        required=False,
        label="Research interests:",
        widget=forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter your research interests",
            }
        ),
    )

    profile_picture = forms.ImageField(
        required=False,
        label="Upload profile picture:",
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
        }),
    )

    profile_picture_url = forms.URLField(
        required=False,
        label="Profile picture URL:",
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "Paste a link to your online image",
        }),
    )


    def clean(self):
        cleaned_data = super().clean()

        # Ensure at least one scientific identifier is provided (ORCID or Scopus)
        orcid = cleaned_data.get("orcid_id")
        scopus = cleaned_data.get("scopus_id")
        if not orcid and not scopus:
            raise forms.ValidationError("Please provide at least one of ORCID ID or Scopus Author ID.")

        # Prevent providing both uploaded image and image URL
        uploaded = cleaned_data.get("profile_picture")
        url = cleaned_data.get("profile_picture_url")

        if uploaded and url:
            raise forms.ValidationError(
                "Please choose either an uploaded picture or a URL, not both."
            )

        return cleaned_data


class ScientistProfileUpdateForm(ScientistProfileForm):
    pass
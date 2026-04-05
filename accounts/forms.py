from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

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

    def clean(self):
        email = self.data.get("username")
        password = self.data.get("password")

        if email and password:

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None


            if user and not user.is_active:
                raise ValidationError(
                    "This account has been deactivated.",
                    code="inactive",
                )


            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )

            if self.user_cache is None:
                raise ValidationError(
                    "Please enter a correct email and password.",
                    code="invalid_login",
                )
            else:
                # Extra Django check (optional but good)
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


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



class UserDeletePreviewForm(forms.ModelForm):
    email = forms.EmailField(
        label="Account email address:",
        disabled=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "readonly": True}),
    )

    full_name = forms.CharField(
        label="Full name:",
        disabled=True,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": True}),
    )

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and hasattr(self.instance, "scientist_profile"):
            self.fields["full_name"].initial = self.instance.scientist_profile.full_name




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
        widget=forms.FileInput(attrs={"class": "form-control"}),
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
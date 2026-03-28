from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView)
from accounts.forms import ScientistProfileForm, CustomAuthenticationForm, UserDeletePreviewForm
from accounts.mixins import ProfileRequiredMixin
from accounts.models import ScientistProfile
from accounts.forms import UserRegisterForm, ScientistProfileUpdateForm
from projects.models import Project

User = get_user_model()

class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'

    # Log in the user after account creation and redirect to complete profile setup
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("profile-create")


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm



class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = ScientistProfile
    form_class = ScientistProfileForm
    template_name = "accounts/profile-create.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("profile-details")



class PublicProfileDetailView(DetailView):
    model = ScientistProfile
    template_name = "accounts/profile-public.html"
    context_object_name = "scientist"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self):
        return get_object_or_404(
            ScientistProfile,
            slug=self.kwargs["slug"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scientist = self.object

        # Retrieve all projects where this scientist participates
        projects = Project.objects.filter(
            memberships__scientist=scientist
        ).distinct()

        context["projects"] = projects

        return context


class ProfileDetailsView(LoginRequiredMixin, ProfileRequiredMixin, DetailView):
    model = ScientistProfile
    template_name = 'accounts/profile-details.html'
    context_object_name = "scientist"

    def get_object(self):
        return get_object_or_404(
            ScientistProfile,
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scientist = self.object

        # Count distinct projects the scientist participates in
        context["project_count"] = (
            scientist.project_memberships
            .values("project")
            .distinct()
            .count()
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, ProfileRequiredMixin, UpdateView):
    model = ScientistProfile
    template_name = 'accounts/profile-update.html'
    form_class = ScientistProfileUpdateForm
    context_object_name = "scientist"

    def get_object(self):
        return get_object_or_404(
            ScientistProfile,
            user=self.request.user
        )

    def form_valid(self, form):
        profile = form.instance

        if self.request.POST.get("remove_picture"):
            profile.profile_picture = None

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("profile-details")


class UserDeleteView(LoginRequiredMixin, ProfileRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/profile-delete.html"
    success_url = reverse_lazy("home")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserDeletePreviewForm(instance=self.object)
        return context

class UserPasswordChangeView(LoginRequiredMixin, ProfileRequiredMixin, PasswordChangeView):
    template_name = "accounts/password-change.html"
    success_url = reverse_lazy("password-change-done")


class UserPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "accounts/password-change-done.html"



class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password-reset.html"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name="accounts/password-reset-done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name="accounts/password-reset-confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name="accounts/password-reset-complete.html"


class ProfilesToReviewView(PermissionRequiredMixin, ListView):
    model = ScientistProfile
    template_name = "accounts/profiles-review-list.html"
    context_object_name = "profiles"
    permission_required = "accounts.can_ban_profile"

    def get_queryset(self):
        return ScientistProfile.objects.filter(is_reviewed=False)


class MarkProfileReviewedView(PermissionRequiredMixin, View):
    permission_required = "accounts.can_ban_profile"

    def post(self, request, slug):
        profile = get_object_or_404(ScientistProfile, slug=slug)

        profile.is_reviewed = True
        profile.save(update_fields=["is_reviewed"])

        return redirect("profiles-review-list")


class BanProfileView(PermissionRequiredMixin, View):
    permission_required = "accounts.can_ban_profile"

    def post(self, request, slug):
        profile = get_object_or_404(ScientistProfile, slug=slug)

        profile.is_reviewed = True
        profile.user.is_active = False

        profile.save(update_fields=["is_reviewed"])
        profile.user.save(update_fields=["is_active"])

        return redirect("profiles-review-list")



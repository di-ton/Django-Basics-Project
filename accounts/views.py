from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from accounts.forms import ScientistProfileForm, CustomAuthenticationForm
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

    def get_success_url(self):
        return reverse("profile-details")


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/profile-delete.html"
    success_url = reverse_lazy("home")

    def get_object(self):
        return self.request.user

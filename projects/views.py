from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView

from feedback.models import Comment
from projects.choices import CategoryChoices
from projects.forms import ProjectCreateForm, ProjectUpdateForm, ArticleCreateForm, \
    ArticleUpdateForm, ScientificEventCreateForm, ScientificEventUpdateForm, ProjectMembershipForm, \
    ScientificOrganizationForm, EventParticipationForm, ProjectDeleteForm, ScientificOrganizationUpdateForm
from projects.mixins import ProjectMixin, EventMixin, ProjectEditMixin
from projects.models import Article, ScientificEvent, Project, ProjectMembership, ScientificOrganization, \
    EventParticipation, ProjectOrganization
from projects.utils import is_content_moderator


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project-create.html'
    form_class = ProjectCreateForm

    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     return super().form_valid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        role = form.cleaned_data["creator_role"]

        ProjectMembership.objects.create(
            project=self.object,
            scientist=self.request.user.scientist_profile,
            name=self.request.user.scientist_profile.full_name,
            email=self.request.user.email,
            role=role
        )

        return response

    # def get_success_url(self):
    #     return reverse(
    #         "project-members-add",
    #         kwargs={"slug": self.object.slug}
    #     )

    def get_success_url(self):
        return reverse("project-overview", kwargs={"slug": self.object.slug})


class ProjectOverviewView(ProjectMixin, TemplateView):
    template_name = "projects/project-overview.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        member_count = project.memberships.filter(role="member").count()
        leader_count = project.memberships.filter(role="leader").count()

        context["members_count"] = member_count + leader_count

        context["articles_count"] = project.articles.count()
        context["events_count"] = project.events.count()

        return context


# class ProjectUpdateView(ProjectMixin, UpdateView):
class ProjectUpdateView(ProjectEditMixin, UpdateView):
    model = Project
    template_name = "projects/project-update.html"
    form_class = ProjectUpdateForm

    def get_success_url(self):
        return reverse("project-overview", kwargs={"slug": self.object.slug})


# class ProjectDeleteView(ProjectMixin, DeleteView):
class ProjectDeleteView(ProjectEditMixin, DeleteView):
    model = Project
    template_name = "projects/project-delete.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ProjectDeleteForm(instance=self.object)
        return context




class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/project-list.html"
    context_object_name = "projects"
    ordering = ["-start_date"]

    def get_queryset(self):
        user = self.request.user
        profile = user.scientist_profile

        projects = Project.objects.filter(
            memberships__scientist=profile,
            is_disabled=False
        ).distinct()

        for project in projects:
            project.user_membership = project.memberships.filter(
                scientist=profile
            ).first()

        return projects

class CategoryListView(TemplateView):
    template_name = "projects/category-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = CategoryChoices.choices
        return context


class ProjectByCategoryView(ListView):
    model = Project
    template_name = "projects/project-by-category.html"
    context_object_name = "projects"

    def get_queryset(self):
        self.category = self.kwargs["category"]

        if self.category not in CategoryChoices.values:
            return Project.objects.none()

        return Project.objects.filter(category=self.category, is_disabled=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_label"] = dict(CategoryChoices.choices).get(
            self.category, self.category
        )
        return context

# class ProjectMembershipCreateView(ProjectMixin, CreateView):
class ProjectMembershipCreateView(ProjectEditMixin, CreateView):
    model = ProjectMembership
    form_class = ProjectMembershipForm
    template_name = "projects/project-membership-form.html"

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        profile = user.scientist_profile
        project = self.get_project()

        if not ProjectMembership.objects.filter(
                project=project,
                email=user.email,
        ).exists():
            initial["name"] = profile.full_name
            initial["email"] = user.email

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.get_project()
        return kwargs

    def form_valid(self, form):
        form.instance.project = self.get_project()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        context["members_added"] = ProjectMembership.objects.filter(
            project=project
        ).order_by("name")

        return context


    def get_success_url(self):
        return reverse(
            "project-members-add",
            kwargs={"slug": self.kwargs["slug"]}
        )


@login_required
def project_member_remove(request, slug, member_id):
    project = get_object_or_404(Project, slug=slug)
    membership = get_object_or_404(
        ProjectMembership,
        pk=member_id,
        project=project,
    )

    # Only users with management rights can remove members
    if not project.can_manage(request.user):
        return HttpResponseForbidden("Not allowed")

    if project.is_disabled:
        return HttpResponseForbidden("Project not available")

    if project.is_locked:
        return HttpResponseForbidden("Project is locked")

    # Prevent removing the project creator
    if membership.scientist and membership.scientist.user == project.created_by:
        return HttpResponseForbidden("Project creator cannot be removed")

    if request.method == "POST":
        membership.delete()

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("project-members", project.slug)


class ProjectMembersView(ProjectMixin, TemplateView):
    template_name = "projects/project-members.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        memberships = project.memberships.select_related("scientist").all()

        leader = memberships.filter(role="leader").first()
        members_qs = memberships.filter(role="member")

        paginator = Paginator(members_qs, 4)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["leader"] = leader
        context["members"] = page_obj
        context["page_obj"] = page_obj
        context["paginator"] = paginator

        return context



class ProjectOrganizationsView(ProjectMixin, ListView):
    model = ProjectOrganization
    template_name = "projects/project-organizations.html"
    context_object_name = "organizations"
    paginate_by = 3

    def get_queryset(self):
        return (
            ProjectOrganization.objects
            .filter(project=self.get_project())
            .select_related("organization")
            .order_by("-is_base_organization", "organization__name")
        )


# class ProjectOrganizationCreateView(ProjectMixin, CreateView):
class ProjectOrganizationCreateView(ProjectEditMixin, CreateView):
    model = ScientificOrganization
    form_class = ScientificOrganizationForm
    template_name = "projects/project-organizations-form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"]["project"] = self.get_project()
        return kwargs

    def form_valid(self, form):
        project = self.get_project()

        organization = form.cleaned_data.get("existing_organization")

        if not organization:
            organization = form.save()

        try:
            ProjectOrganization.objects.create(
                project=project,
                organization=organization,
                is_base_organization=form.cleaned_data["is_base_organization"]
            )
        except IntegrityError:
            form.add_error(
                "is_base_organization",
                "This project already has a base organization."
            )
            return self.form_invalid(form)

        return redirect("project-organizations", slug=project.slug)


class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    model = ScientificOrganization
    form_class = ScientificOrganizationUpdateForm
    template_name = "projects/project-organization-update.html"

    def dispatch(self, request, *args, **kwargs):
        if not is_content_moderator(request.user):
            return HttpResponseForbidden("Not allowed")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get("next") or reverse("home")



@login_required
def project_organization_remove(request, slug, organization_id):
    project = get_object_or_404(Project, slug=slug)

    project_org = get_object_or_404(
        ProjectOrganization,
        pk=organization_id,
        project=project
    )

    if not project.can_manage(request.user):
        return HttpResponseForbidden("Not allowed")

    if project.is_disabled:
        return HttpResponseForbidden("Project not available")

    if project.is_locked:
        return HttpResponseForbidden("Project is locked")

    if request.method == "POST":
        project_org.delete()

    return redirect("project-organizations", project.slug)


class ProjectArticlesView(ProjectMixin, ListView):
    template_name = "projects/project-articles.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(project=self.get_project()).order_by("-publication_year")


class ArticleCreateView(ProjectMixin, CreateView):
# class ArticleCreateView(ProjectEditMixin, CreateView):
    model = Article
    form_class = ArticleCreateForm
    template_name = "articles/article-form.html"

    def form_valid(self, form):
        form.instance.project = self.get_project()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "project-articles",
            kwargs={"slug": self.object.project.slug},
        )

# class ArticleUpdateView(ProjectMixin, UpdateView):
class ArticleUpdateView(ProjectEditMixin, UpdateView):
    model = Article
    form_class = ArticleUpdateForm
    template_name = "articles/article-form.html"

    # Ensure only objects related to this project are retrieved
    def get_queryset(self):
        return Article.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-articles",
            kwargs={"slug": self.object.project.slug},
        )


# class ArticleDeleteView(ProjectMixin, DeleteView):
class ArticleDeleteView(ProjectEditMixin, DeleteView):
    model = Article
    template_name = "articles/article-delete.html"

    def get_queryset(self):
        # only delete articles from this project
        return Article.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-articles",
            kwargs={"slug": self.object.project.slug},
        )



class ProjectEventsView(ProjectMixin, ListView):
    model = ScientificEvent
    template_name = "projects/project-events.html"
    context_object_name = "events"

    def get_queryset(self):
        return ScientificEvent.objects.filter(project=self.get_project()).order_by("-start_date")


# class EventCreateView(ProjectMixin, CreateView):
class EventCreateView(ProjectEditMixin, CreateView):
    model = ScientificEvent
    form_class = ScientificEventCreateForm
    template_name = "events/event-form.html"

    def form_valid(self, form):
        form.instance.project = self.get_project()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "project-events",
            kwargs={"slug": self.object.project.slug},
        )


# class EventUpdateView(ProjectMixin, UpdateView):
class EventUpdateView(ProjectEditMixin, UpdateView):
    model = ScientificEvent
    form_class = ScientificEventUpdateForm
    template_name = "events/event-form.html"

    def get_queryset(self):
        return ScientificEvent.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-events",
            kwargs={"slug": self.object.project.slug},
        )

# class EventDeleteView(ProjectMixin, DeleteView):
class EventDeleteView(ProjectEditMixin, DeleteView):
    model = ScientificEvent
    template_name = "events/event-delete.html"
    context_object_name = "event"

    def get_queryset(self):
        return ScientificEvent.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-events",
            kwargs={"slug": self.object.project.slug},
        )


# class EventParticipationCreateView(ProjectMixin, EventMixin, CreateView):
class EventParticipationCreateView(ProjectEditMixin, EventMixin, CreateView):
    model = EventParticipation
    form_class = EventParticipationForm
    template_name = "events/participation-form.html"

    def form_valid(self, form):
        form.instance.event = self.get_event()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "project-events",
            kwargs={"slug": self.object.event.project.slug},
        )


# class EventParticipationDeleteView(ProjectMixin, EventMixin, DeleteView):
class EventParticipationDeleteView(ProjectEditMixin, EventMixin, DeleteView):
    model = EventParticipation
    template_name = "events/participation-delete.html"

    def get_queryset(self):
        return EventParticipation.objects.filter(
            event=self.get_event()
        )

    def get_success_url(self):
        return reverse(
            "project-events",
            kwargs={"slug": self.object.event.project.slug},
        )


class ProjectCommentsView(ProjectMixin, DetailView):
    model = Project
    template_name = "feedback/project-comments.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self):
        return self.get_project()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["comments"] = Comment.objects.filter(
            project=self.object,
            parent__isnull=True
        ).select_related("user").prefetch_related("replies")

        return context


@login_required
def lock_project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not is_content_moderator(request.user):
        return HttpResponseForbidden("Not allowed")

    project.is_locked = True
    project.save()

    return redirect("project-overview", slug=slug)


@login_required
def unlock_project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not is_content_moderator(request.user):
        return HttpResponseForbidden()

    project.is_locked = False
    project.save()

    return redirect("project-overview", slug=slug)


@login_required
def disable_project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not is_content_moderator(request.user):
        return HttpResponseForbidden()

    note = request.POST.get("moderation_note")

    project.is_disabled = True
    project.disabled_by = request.user
    project.moderation_note = note
    project.save()

    return redirect("project-overview", slug=slug)


@login_required
def enable_project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not is_content_moderator(request.user):
        return HttpResponseForbidden()

    project.is_disabled = False
    project.save()

    return redirect("project-overview", slug=slug)









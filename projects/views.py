from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView

from projects.choices import CategoryChoices
from projects.forms import ProjectCreateForm, ProjectUpdateForm, ArticleCreateForm, \
    ArticleUpdateForm, ScientificEventCreateForm, ScientificEventUpdateForm, ProjectMembershipForm, \
    ScientificOrganizationForm, EventParticipationForm, ProjectDeleteForm
from projects.mixins import ProjectMixin, EventMixin
from projects.models import Article, ScientificEvent, Project, ProjectMembership, ScientificOrganization, \
    EventParticipation


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = "projects/project-form.html"
    form_class = ProjectCreateForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "project-members-add",
            kwargs={"slug": self.object.slug}
        )


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


class ProjectUpdateView(ProjectMixin, UpdateView):
    model = Project
    template_name = "projects/project-form.html"
    form_class = ProjectUpdateForm

    def get_success_url(self):
        return reverse("project-overview", kwargs={"slug": self.object.slug})


class ProjectDeleteView(ProjectMixin, DeleteView):
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

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Project.objects.none()

        profile = user.scientist_profile

        projects = Project.objects.filter(
            memberships__scientist=profile
        ).distinct()

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

        return Project.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_label"] = dict(CategoryChoices.choices).get(
            self.category, self.category
        )
        return context


class ProjectMembershipCreateView(ProjectMixin, CreateView):
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

    if not project.can_manage(request.user):
        return HttpResponseForbidden("Not allowed")

    if membership.scientist and membership.scientist.user == project.created_by:
        return HttpResponseForbidden("Project creator cannot be removed")

    if request.method == "POST":
        membership.delete()

    return redirect("project-members", project.slug)



class ProjectMembersView(ProjectMixin, TemplateView):
    template_name = "projects/project-members.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        memberships = project.memberships.select_related("scientist")

        context["leader"] = memberships.filter(role="leader").first()
        context["members"] = memberships.filter(role="member")
        context["can_manage"] = project.can_manage(self.request.user)

        return context



class ProjectOrganizationsView(ProjectMixin, ListView):
    model = ScientificOrganization
    template_name = "projects/project-organizations.html"
    context_object_name = "organizations"

    def get_queryset(self):
        return self.get_project().organizations.all().order_by('-is_base_organization', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = self.get_project().can_manage(self.request.user)
        return context


class ProjectOrganizationCreateView(ProjectMixin, CreateView):
    model = ScientificOrganization
    form_class = ScientificOrganizationForm
    template_name = "projects/project-organizations-form.html"


    def form_valid(self, form):
        project = self.get_project()
        name = form.cleaned_data["name"]

        try:
            self.object = form.save()
        except IntegrityError:
            self.object = ScientificOrganization.objects.get(
                name__iexact=name
            )

            for field in ["country", "address", "website", "is_base_organization"]:
                setattr(self.object, field, form.cleaned_data.get(field))

            self.object.save()


        project.organizations.add(self.object)

        return redirect("project-organizations", slug=project.slug)


@login_required
def project_organization_remove(request, slug, organization_id):
    project = get_object_or_404(Project, slug=slug)
    organization = get_object_or_404(ScientificOrganization, pk=organization_id)

    if not project.can_manage(request.user):
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        project.organizations.remove(organization)

    return redirect("project-organizations", project.slug)











class ProjectArticlesView(ProjectMixin, ListView):
    template_name = "projects/project-articles.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(project=self.get_project()).order_by("-publication_year")



class ArticleCreateView(ProjectMixin, CreateView):
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


class ArticleUpdateView(ProjectMixin, UpdateView):
    model = Article
    form_class = ArticleUpdateForm
    template_name = "articles/article-form.html"

    def get_queryset(self):
        return Article.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-articles",
            kwargs={"slug": self.object.project.slug},
        )

class ArticleDeleteView(ProjectMixin, DeleteView):
    model = Article
    template_name = "articles/article-delete.html"

    def get_queryset(self):
        # SECURITY: only allow deleting articles from this project
        return Article.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-articles",
            kwargs={"slug": self.object.project.slug},
        )



class ProjectEventsView(ProjectMixin, ListView):
    model = ScientificEvent
    template_name = "projects/project_events.html"
    context_object_name = "events"

    def get_queryset(self):
        return ScientificEvent.objects.filter(project=self.get_project())


class EventCreateView(ProjectMixin, CreateView):
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



class EventUpdateView(ProjectMixin, UpdateView):
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

class EventDeleteView(ProjectMixin, DeleteView):
    model = ScientificEvent
    template_name = "events/event-delete.html"

    def get_queryset(self):
        return ScientificEvent.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-events",
            kwargs={"slug": self.object.project.slug},
        )



class EventParticipationCreateView(ProjectMixin, EventMixin, CreateView):
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


class EventParticipationDeleteView(ProjectMixin, EventMixin, DeleteView):
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




















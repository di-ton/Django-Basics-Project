from django.urls import reverse
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from projects.forms import ProjectCreateForm, ProjectUpdateForm, ProjectMembersForm, ArticleCreateForm, \
    ArticleUpdateForm, ScientificEventCreateForm, ScientificEventUpdateForm
from projects.mixins import ProjectMixin, ProjectWritePermissionMixin
from projects.models import Article, ScientificEvent, Project


class ProjectCreateView(CreateView):
    model = Project
    template_name = "projects/project-form.html"
    form_class = ProjectCreateForm



class ProjectOverviewView(ProjectMixin, TemplateView):
    template_name = "projects/project-overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        context["member_count"] = project.members.count()
        context["articles_count"] = project.articles.count()
        context["visited_events"] = project.events.count()

        return context


class ProjectUpdateView(ProjectMixin, UpdateView):
    model = Project
    template_name = "projects/project-form.html"
    form_class = ProjectUpdateForm

    def get_success_url(self):
        return reverse("project-members-manage", kwargs={"slug": self.object.slug})


class ProjectMembersUpdateView(ProjectMixin, UpdateView):
    model = Project
    form_class = ProjectMembersForm
    template_name = "projects/project-members-form.html"

    def get_success_url(self):
        return reverse("projects-members", kwargs={"slug": self.object.slug})


class ProjectMembersView(ProjectMixin, ListView):
    template_name = "projects/project-members.html"
    context_object_name = "members"

    def get_queryset(self):
        return self.get_project().members.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["leader"] = self.get_project().leader
        return context


class ProjectArticlesView(ProjectMixin, ListView):
    template_name = "projects/project-articles.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(project=self.get_project())



class ProjectEventsView(ProjectMixin, ListView):
    model = ScientificEvent
    template_name = "projects/project_events.html"
    context_object_name = "events"

    def get_queryset(self):
        return ScientificEvent.objects.filter(project=self.get_project())



class ArticleCreateView(ProjectWritePermissionMixin, ProjectMixin, CreateView):
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


class ArticleUpdateView(ProjectWritePermissionMixin, ProjectMixin, UpdateView):
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

class ArticleDeleteView(ProjectWritePermissionMixin, ProjectMixin, DeleteView):
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


class EventCreateForm:
    pass


class EventCreateView(ProjectWritePermissionMixin, ProjectMixin, CreateView):
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


class EventUpdateForm:
    pass


class EventUpdateView(ProjectWritePermissionMixin, ProjectMixin, UpdateView):
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

class EventDeleteView(ProjectWritePermissionMixin, ProjectMixin, DeleteView):
    model = ScientificEvent
    template_name = "events/event-delete.html"

    def get_queryset(self):
        return ScientificEvent.objects.filter(project=self.get_project())

    def get_success_url(self):
        return reverse(
            "project-events",
            kwargs={"slug": self.object.project.slug},
        )




























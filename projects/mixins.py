from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from .models import Project, ScientificEvent
from .utils import is_content_moderator


class ProjectMixin:

    def get_project(self):
        project = get_object_or_404(Project, slug=self.kwargs["slug"])

        if project.is_disabled and not is_content_moderator(self.request.user):
            raise Http404("Project not available")

        return project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()

        context["project"] = project
        context["can_manage"] = project.can_manage(self.request.user)

        return context



class ProjectEditMixin(ProjectMixin):

    def get_project_for_edit(self):
        return self.get_project()

    def post(self, request, *args, **kwargs):
        project = self.get_project_for_edit()

        if not project.is_editable():
            messages.error(
                request,
                "This project is currently locked and cannot be modified."
            )
            return redirect("project-overview", slug=project.slug)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        project = self.get_project_for_edit()

        if not project.is_editable():
            messages.error(
                self.request,
                "This project is currently locked and cannot be modified."
            )
            return redirect("project-overview", slug=project.slug)

        return super().form_valid(form)


class EventMixin:
    def get_event(self):
        if not hasattr(self, "_event"):
            self._event = get_object_or_404(
                ScientificEvent,
                pk=self.kwargs["event_pk"]
            )
        return self._event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.get_event()
        return context

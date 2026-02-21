from django.shortcuts import get_object_or_404
from .models import Project, ScientificEvent


class ProjectMixin:
    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()

        context["project"] = project
        context["can_manage"] = project.can_manage(self.request.user)

        return context



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

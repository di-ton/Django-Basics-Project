from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Project

class ProjectMixin:
    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.get_project()
        return context


class ProjectWritePermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        project = self.get_project()
        profile = request.user.scientistprofile

        if profile != project.leader and not project.members.filter(pk=profile.pk).exists():
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)


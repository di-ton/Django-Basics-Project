from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from accounts.models import ScientistProfile
from projects.models import Project


class HomePageView(ListView):
    model = Project
    template_name = "common/home-page.html"
    context_object_name = "projects"
    ordering = ["-start_date"]
    paginate_by = 4

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("created_by")
            .prefetch_related(
                "memberships",
                "memberships__scientist",
            )
        )



class ProjectSearchView(TemplateView):
    template_name = "common/search-results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("text")

        projects = Project.objects.none()
        profiles = ScientistProfile.objects.none()

        if query:
            projects = Project.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(memberships__name__icontains=query) |
                Q(keywords__icontains=query) |
                Q(project_number__exact=query) |
                Q(organizations__name__icontains=query)
            ).distinct()

            profiles = ScientistProfile.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).distinct()

        context["projects"] = projects
        context["profiles"] = profiles
        context["query"] = query

        return context


from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from common.forms import SearchForm
from projects.models import Project


# class HomePageView(TemplateView):
#     template_name = "common/home-page.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["search_form"] = SearchForm(self.request.GET or None)
#         return context


class HomePageView(ListView):
    model = Project
    template_name = "common/home-page.html"
    context_object_name = "projects"
    ordering = ["-created_at"]
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

class ProjectSearchView(ListView):
    model = Project
    template_name = "common/search-results.html"
    context_object_name = "projects"

    def get_queryset(self):
        projects = Project.objects.all()

        query = self.request.GET.get("text")
        if query:
            projects = projects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(memberships__name__icontains=query)
            ).distinct()

        return projects.distinct()


from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from common.forms import SearchForm


class HomePageView(TemplateView):
    template_name = "common/home-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(self.request.GET or None)
        return context


# class HomePageView(ListView):
#     model = Project
#     template_name = "common/home-page.html"
#     context_object_name = "pojects"
#     paginate_by = 10

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     kwargs.update({
    #         "comment_form": CommentBaseForm(),
    #         "search_form": SearchForm(),
    #     })
    #     return super().get_context_data(object_list=object_list, **kwargs)
    #
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     pet_name = self.request.GET.get("text")
    #
    #     if pet_name:
    #         queryset = (queryset.prefetch_related("tagged_pets", "like_set").filter(
    #             tagged_pets__name__icontains=pet_name
    #         ))
    #     return queryset

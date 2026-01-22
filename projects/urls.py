from django.urls import path, include
from projects import views


urlpatterns = [
    path("", views.ProjectCreateView.as_view(), name="project-create"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/<str:category>/", views.ProjectByCategoryView.as_view(), name="project-by-category"),
    path("<slug:slug>/", include([
        path("", views.ProjectOverviewView.as_view(), name="project-overview"),

        path("members/", views.ProjectMembersView.as_view(), name="project-members"),
        path("members/update/", views.ProjectMembersUpdateView.as_view(), name="project-members-update"),

        path("articles/", views.ProjectArticlesView.as_view(), name="project-articles"),
        path("articles/add/", views.ArticleCreateView.as_view(), name="project-article-add"),
        path("articles/<int:pk>/edit/", views.ArticleUpdateView.as_view(), name="project-article-edit"),
        path("articles/<int:pk>/delete/", views.ArticleDeleteView.as_view(), name="project-article-delete"),

        path("events/", views.ProjectEventsView.as_view(), name="project-events"),
        path("events/add/", views.EventCreateView.as_view(), name="project-event-add"),
        path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="project-event-edit"),
        path("events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="project-event-delete"),

    ])),
]

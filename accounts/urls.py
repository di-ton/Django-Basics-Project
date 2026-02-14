from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from accounts import views

urlpatterns = [
    # Registration and Authentication
    path("register/", views.RegisterView.as_view(), name="register"),
    path("create/", views.ProfileCreateView.as_view(), name="profile-create"),
    path("login/", views.UserLoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Own profile
    path("", views.ProfileDetailsView.as_view(), name="profile-details"),
    path("update/", views.ProfileUpdateView.as_view(), name="profile-update"),
    path("delete/", views.UserDeleteView.as_view(), name="profile-delete"),

    # Public profile by slug
    path("<slug:slug>/", views.PublicProfileDetailView.as_view(), name="profile-public",
    )
]

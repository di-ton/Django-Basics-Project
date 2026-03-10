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
    
    # Password change
    path("password-change/", views.UserPasswordChangeView.as_view(), name="password-change"),
    path("password-change/done/", views.UserPasswordChangeDoneView.as_view(), name="password-change-done"),
    
    # Password reset
    path("password-reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    
    
    # Profile moderation
    path("moderation/", views.ProfilesToReviewView.as_view(), name="profiles-review-list"),
    path("moderation/<slug:slug>/review/", views.MarkProfileReviewedView.as_view(), name="profile-review"),
    path("moderation/<slug:slug>/ban/", views.BanProfileView.as_view(), name="profile-ban"),

    # Public profile by slug
    path("<slug:slug>/", views.PublicProfileDetailView.as_view(), name="profile-public"),

]

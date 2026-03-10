from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from accounts.models import ScientistProfile

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

@admin.register(ScientistProfile)
class ScientistProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "academic_degree",
        "affiliation",
        "is_reviewed",
        "is_approved",
    )
    list_filter = ("is_reviewed", "is_approved", "academic_degree")
    search_fields = ("user__email", "first_name", "last_name")

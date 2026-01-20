from django.contrib import admin

from accounts.models import ScientistProfile


@admin.register(ScientistProfile)
class ScientistProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "academic_degree", "affiliation")

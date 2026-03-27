from django.contrib import admin

from projects.models import ScientificOrganization, Project, ProjectMembership, Article, ScientificEvent, \
    EventParticipation, ProjectOrganization


@admin.register(ScientificOrganization)
class ScientificOrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("country",)



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "acronym", "status", "category", "created_by")
    list_filter = ("status", "category")
    search_fields = ("title", "acronym", "keywords", "project_number")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ProjectOrganization)
class ProjectOrganizationAdmin(admin.ModelAdmin):
    list_display = ("project", "organization", "is_base_organization")
    list_filter = ("is_base_organization",)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "name", "role", "scientist")
    list_filter = ("role",)
    search_fields = ("name", "email", "project__title")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "journal", "publication_year")
    list_filter = ("publication_year", "journal_quartile")
    search_fields = ("title", "journal", "authors", "doi")


@admin.register(ScientificEvent)
class ScientificEventAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "start_date", "end_date")
    list_filter = ("start_date",)
    search_fields = ("name", "location")


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "participation_type")
    list_filter = ("participation_type",)
    search_fields = ("title", "authors")



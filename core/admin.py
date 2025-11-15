from django.contrib import admin

from .models import (
    Partner, Client, Project,
    Environment, Server, Resource,
    UserProfile, Issue, InfraActivity,
)


# ---------- Inlines ----------

class ClientInline(admin.TabularInline):
    model = Client
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


class EnvironmentInline(admin.TabularInline):
    model = Environment
    extra = 0


class ServerInline(admin.TabularInline):
    model = Server
    extra = 0


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0


class InfraActivityInline(admin.TabularInline):
    model = InfraActivity
    extra = 0
    fields = ("activity_date", "status", "note", "hours_spent")
    readonly_fields = ("created_at",)


# ---------- Admin classes ----------

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "contact_person", "contact_email", "active", "created_at")
    list_filter = ("active", "created_at")
    search_fields = ("name", "code", "contact_person", "contact_email")
    ordering = ("name",)
    readonly_fields = ("created_at",)
    inlines = [ClientInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "partner", "code", "contact_person", "contact_email", "active", "created_at")
    list_filter = ("partner", "active", "created_at")
    search_fields = ("name", "code", "partner__name")
    ordering = ("partner", "name")
    readonly_fields = ("created_at",)
    inlines = [ProjectInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "code", "is_active", "created_at")
    list_filter = ("client__partner", "client", "is_active")
    search_fields = ("name", "code", "client__name", "client__partner__name")
    ordering = ("client", "name")
    readonly_fields = ("created_at",)
    inlines = [EnvironmentInline]


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "env_type", "base_url", "is_active", "created_at")
    list_filter = ("env_type", "is_active", "project__client", "project__client__partner")
    search_fields = ("name", "project__name", "project__client__name", "project__client__partner__name")
    ordering = ("project", "env_type", "name")
    readonly_fields = ("created_at",)
    inlines = [ServerInline, ResourceInline]


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "environment", "provider", "region", "ip_address", "ssh_user", "ssh_port", "is_active", "created_at")
    list_filter = ("provider", "is_active", "environment__env_type", "environment__project__client")
    search_fields = ("name", "ip_address", "environment__name", "environment__project__name")
    ordering = ("environment", "name")
    readonly_fields = ("created_at",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "environment", "resource_type", "provider", "identifier", "is_critical", "is_active", "created_at")
    list_filter = ("resource_type", "provider", "is_critical", "is_active")
    search_fields = ("name", "identifier", "environment__name", "environment__project__name")
    ordering = ("environment", "resource_type", "name")
    readonly_fields = ("created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "partner", "client", "role")
    list_filter = ("partner", "client", "role")
    search_fields = ("user__username", "user__email", "role")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "title", "project", "environment", "resource",
        "status", "priority",
        "activity_date", "due_date",
        "estimate_hours", "actual_hours",
        "delay_display",
        "assigned_to", "project_manager",
        "created_at",
    )
    list_filter = (
        "status", "priority",
        "project__client__partner",
        "project__client",
        "project",
        "environment__env_type",
        "assigned_to",
        "project_manager",
    )
    search_fields = (
        "title", "description",
        "project__name",
        "project__client__name",
        "project__client__partner__name",
        "environment__name",
        "resource__name",
    )
    date_hierarchy = "activity_date"
    readonly_fields = ("created_at", "updated_at")
    inlines = [InfraActivityInline]
    autocomplete_fields = ("project", "environment", "resource", "assigned_to", "assigned_by", "project_manager")

    def delay_display(self, obj):
        return obj.delay_days

    delay_display.short_description = "Delay (days)"


@admin.register(InfraActivity)
class InfraActivityAdmin(admin.ModelAdmin):
    list_display = (
        "issue", "activity_date", "status",
        "hours_spent", "created_at",
    )
    list_filter = ("activity_date", "status", "issue__project")
    search_fields = ("issue__title", "note")
    readonly_fields = ("created_at",)

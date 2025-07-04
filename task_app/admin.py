from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *




@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
    list_display = ("email", "username", "id", "first_name", "last_name", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "owner__username", "owner__email")
    list_filter = ("created_at",)


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role")
    list_filter = ("role",)
    search_fields = ("project__name", "user__username", "user__email")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "assigned_to", "due_date")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description", "assigned_to__username", "project__name")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("task", "user", "created_at")
    search_fields = ("task__title", "user__username", "content")
    list_filter = ("created_at",)

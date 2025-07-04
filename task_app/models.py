from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager





class UserManager(BaseUserManager):
    def create_user(self, email, username, password, first_name="", last_name="", **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            date_joined=timezone.now(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username    = models.CharField(max_length=150, unique=True)
    email       = models.EmailField(max_length=100, unique=True)
    first_name  = models.CharField(max_length=30, blank=True)
    last_name   = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username



class Project(models.Model):
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner       = models.ForeignKey(
        User,
        related_name="owned_projects",
        on_delete=models.CASCADE,
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class ProjectMember(models.Model):
    ADMIN  = "admin"
    MEMBER = "member"
    ROLE_CHOICES = [(ADMIN, "Admin"), (MEMBER, "Member")]

    project = models.ForeignKey(
        Project, related_name="members", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="project_memberships",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)

    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user} ➜ {self.project} ({self.role})"



class Task(models.Model):
    TODO        = "todo"
    IN_PROGRESS = "in_progress"
    DONE        = "done"
    STATUS_CHOICES = [(TODO, "To Do"), (IN_PROGRESS, "In Progress"), (DONE, "Done")]

    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"
    PRIORITY_CHOICES = [(LOW, "Low"), (MEDIUM, "Medium"), (HIGH, "High")]

    project      = models.ForeignKey(
        Project, related_name="tasks", on_delete=models.CASCADE
    )
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    status       = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=TODO
    )
    priority     = models.CharField(
        max_length=6, choices=PRIORITY_CHOICES, default=MEDIUM
    )
    assigned_to  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="tasks",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    due_date     = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.project}] {self.title}"



class Comment(models.Model):
    task       = models.ForeignKey(
        Task, related_name="comments", on_delete=models.CASCADE
    )
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="comments", on_delete=models.CASCADE
    )
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} ➜ {self.task}"


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_nested.routers import NestedDefaultRouter
from . import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'projects', views.ProjectViewSet, basename='projects')
router.register(r'project_members', views.ProjectMemberViewSet, basename='project_members')
router.register(r'tasks', views.TaskViewSet, basename='tasks')
router.register(r'comments', views.CommentViewSet, basename='comments')

projects_router = NestedDefaultRouter(router, r'projects', lookup='project')
projects_router.register(r'tasks', views.TaskViewSet, basename='project-tasks')

tasks_router = NestedDefaultRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', views.CommentViewSet, basename='task-comments')

urlpatterns = [
    path("users/register/", views.RegisterView.as_view(), name="register"),
    path("users/login/", views.LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("", include(router.urls)),
    path("", include(projects_router.urls)),
    path("", include(tasks_router.urls)),
]
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from .serializers import *
from .models import *

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Only allow users to access/update their own user object.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user
    

class IsTaskEditor(BasePermission):
    """
    ─ create/list/retrieve ────────── any authenticated user (handled in has_permission)
    ─ update/partial_update ──────── superuser OR project‑member OR assigned user
    ─ destroy ────────────────────── superuser OR project‑member
    """
    def has_permission(self, request, view):
        # Every authenticated user may hit the view;
        # object‑level rules apply afterwards.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Everyone can read
        if request.method in SAFE_METHODS:
            return True

        # ----- superuser: always win -----
        if request.user.is_superuser:
            return True

        # Is the caller a member of this project?
        is_proj_member = obj.project.members.filter(id=request.user.id).exists()

        if request.method == "DELETE":
            # Delete: superuser OR any project member
            return is_proj_member

        # Update / partial_update:
        if is_proj_member:
            return True            # project member allowed
        return obj.assigned_to_id == request.user.id  # assignee allowed
    

class IsSelfOrAdminForDeleteOnly(BasePermission):
    """
    - GET / PUT / PATCH: allowed if user is object owner
    - DELETE: only superuser can delete any user
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.is_superuser

        # Allow GET, PUT, PATCH if the user is viewing/updating their own profile
        return obj == request.user
    

class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsSelfOrAdminForDeleteOnly]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        user.delete()
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": "Listing users is not allowed."},
            status=status.HTTP_403_FORBIDDEN
        )
    

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Project created successfully",
            "data": response.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if project.owner != request.user:
            return Response({
                "message": "You do not have permission to update this project."
            }, status=status.HTTP_403_FORBIDDEN)

        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Project updated successfully",
            "data": response.data
        })

    def partial_update(self, request, *args, **kwargs):
        project = self.get_object()
        if project.owner != request.user:
            return Response({
                "message": "You do not have permission to update this project."
            }, status=status.HTTP_403_FORBIDDEN)

        response = super().partial_update(request, *args, **kwargs)
        return Response({
            "message": "Project updated successfully",
            "data": response.data
        })

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.owner != request.user:
            return Response({
                "message": "You do not have permission to delete this project."
            }, status=status.HTTP_403_FORBIDDEN)

        project.delete()
        return Response({
            "message": "Project deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)
        
        
class ProjectMemberViewSet(viewsets.ModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Project member added successfully",
            "data": response.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Project member updated successfully",
            "data": response.data
        })

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response({
            "message": "Project member updated successfully",
            "data": response.data
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Project member removed successfully"
        }, status=status.HTTP_204_NO_CONTENT)
        
        
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("project", "assigned_to")
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskEditor]

    # Optional nested route support: /projects/<project_pk>/tasks/
    def get_queryset(self):
        project_id = self.kwargs.get("project_pk")
        base_qs = super().get_queryset()
        return base_qs.filter(project_id=project_id) if project_id else base_qs

    # Success‑message wrappers
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response({"message": "Task created successfully", "data": resp.data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        return Response({"message": "Task updated successfully", "data": resp.data})

    def partial_update(self, request, *args, **kwargs):
        resp = super().partial_update(request, *args, **kwargs)
        return Response({"message": "Task updated successfully", "data": resp.data})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Task deleted successfully"},
                        status=status.HTTP_204_NO_CONTENT)
        
        
class CommentViewSet(viewsets.ModelViewSet):
    """
    • list   /comments/                     (all authenticated)
    • list   /tasks/<task_pk>/comments/     (nested)
    • create /tasks/<task_pk>/comments/     (sets user & task automatically)
    • retrieve /comments/<id>/
    • update /comments/<id>/
    • destroy /comments/<id>/
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Comment.objects.select_related('user', 'task')
        task_id = self.kwargs.get('task_pk')
        return qs.filter(task_id=task_id) if task_id else qs

    def perform_create(self, serializer):
        # Assign the comment to the current user and, if nested, the parent task
        task_id = self.kwargs.get('task_pk')
        serializer.save(user=self.request.user, task_id=task_id)

    # Success‑message wrappers:
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Comment created successfully", "data": resp.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        return Response({"message": "Comment updated successfully", "data": resp.data})

    def partial_update(self, request, *args, **kwargs):
        resp = super().partial_update(request, *args, **kwargs)
        return Response({"message": "Comment updated successfully", "data": resp.data})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsSelfOrReadOnly]

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
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        return Response({"detail": "Listing users is not allowed."}, status=403)
    
    
# class ProjectViewSet(viewsets.ModelViewSet):
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)


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

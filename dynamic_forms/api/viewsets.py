from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from dynamic_forms.models import *
from .serializers import *
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status





class ManageFormViewSet(viewsets.ModelViewSet): #CRUD
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)


class ManageProcessViewSet(viewsets.ModelViewSet): #CRUD
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)



class ProcessListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.exclude(owner=self.request.user)



class ManageCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Admin can access all categories, others only their own
        if self.request.user.is_staff:
            return Category.objects.all()
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the owner to the current user
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Allow updates only if the current user is the owner or admin
        if self.request.user != serializer.instance.owner and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to edit this category.")
        serializer.save()

    def perform_destroy(self, instance):
        # Allow deletion only if the current user is the owner or admin
        if self.request.user != instance.owner and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to delete this category.")
        instance.delete()


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

    @action(detail=True, methods=['post'])
    def response(self, request, pk=None):
        process_instance = get_object_or_404(Process, pk=pk)

        password = request.data.get('password')

        if password == process_instance.password or process_instance.password == "":
            request.session[f'verified_process_{pk}'] = True
            return Response({"detail": "Moving to questions."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Incorrect password."}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['get'])
    def show_questions(self, request, pk=None):
        if not request.session.get(f'verified_process_{pk}', False):
            return Response({"detail": "Password verification required."}, status=status.HTTP_403_FORBIDDEN)

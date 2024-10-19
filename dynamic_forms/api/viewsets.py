from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from dynamic_forms.models import *
from .serializers import *
from django.db.models import Q





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



from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework import response
from dynamic_forms.models import *
from .serializers import *
from django.db.models import Q




class ManageQuestionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(form__owner=self.request.user)



class ManageFormViewSet(viewsets.ModelViewSet): #CRUD
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)

    @action(detail=True, methods=['GET','POST'])
    def questions(self, request, pk=None):
        if request.method == "POST":
            serializer = QuestionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                form = self.get_object()
                serializer.save(form=form)
                return response.Response(serializer.data, status=201)
            return response.Response(serializer.errors, status=400)

        form = self.get_object()
        questions = Question.objects.filter(form=form)
        serializer = QuestionSerializer(questions, many=True, context={'request': request})
        return response.Response(serializer.data)


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

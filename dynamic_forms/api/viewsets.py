from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework import response
from dynamic_forms.models import *
from .serializers import *
from django.db.models import Q

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(username=self.request.user.username)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context



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

    def get_serializer_class(self):
            if self.action == 'questions':
                return QuestionSerializer
            return super().get_serializer_class()

    @action(detail=True, methods=['GET','POST'])
    def questions(self, request, pk=None):
        form = self.get_object()

        if request.method == "POST":
            serializer = QuestionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(form=form)
                return response.Response(serializer.data, status=201)
            return response.Response(serializer.errors, status=400)

        questions = Question.objects.filter(form=form)
        serializer = QuestionSerializer(questions, many=True, context={'request': request})
        return response.Response(serializer.data)



class ManageProcessViewSet(viewsets.ModelViewSet): #CRUD
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)



class ProcessListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.exclude(owner=self.request.user)

    def retrieve(self, request, pk=None):
        process = self.get_object()
        user = request.user
        WatchProcessHistory.objects.create(user=user, process=process)
        serializer = self.get_serializer(process)
        return response.Response(serializer.data)

    @action(detail=True, methods=['GET','POST'], url_path='answer(?:/(?P<form_id>[^/.]+))?')
    def answer(self, request:HttpRequest, pk=None, form_id=None):
        process_instance = self.get_object()

        if request.method == "POST":
            if not process_instance.is_public():
                check_password = ""
                password = request.data.get('password')
                if password:
                    check_password = password
                    request.session[f'verified_process_{pk}'] = password
                else:
                    check_password = request.session.get(f'verified_process_{pk}', "")
                if check_password != process_instance.password:
                    return response.Response(
                        {"detail": "Incorrect password. Send the correct password!"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )

            responses = request.data.get('response')
            if responses:
                if process_instance.type == "linear":
                    curr_positoin = request.session.get(f'lst_pos_process_{pk}',0) + 1
                    position_instance = get_object_or_404(
                        FormPosition,Q(process=process_instance)&Q(position=curr_positoin)
                    )
                    form = position_instance.form
                else:
                    forms = process_instance.forms.all()
                    try:
                        form = forms.get(id=form_id)
                    except:
                        return response.Response({"detail": "this form-id dose not exist!"}, status=status.HTTP_404_NOT_FOUND)
        
                questions = form.questions.all()

                questions_id = [x.id for x in questions]
                responses_id = [_response['id'] for _response in responses]
                if len(questions_id) != len(responses_id):
                    return response.Response(
                        {"error":"response is not valid (len)!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                responses_id = list(set(responses_id))
                if questions_id != responses_id:
                    return response.Response(
                        {"error":"response is not valid (set)!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                validate_answer = []
                for _response in responses:
                    answer = str(_response['answer'])
                    question = get_object_or_404(Question,pk=_response['id'])

                    res_serializer = ResopnseSerializer(
                        data={"question":question.id,"answer":answer}
                    )
                    if res_serializer.is_valid(raise_exception=True):
                        validate_answer.append(res_serializer)

                user = request.user
                for answer in validate_answer:
                    answer.save(user=user)


                if process_instance.type == "linear":
                    curr_pos = request.session.get(f'lst_pos_process_{pk}',0) + 1
                    count_positions = process_instance.positions.all().count()

                    if count_positions <= curr_pos:
                        request.session[f'lst_pos_process_{pk}'] = 0
                        return response.Response({"detail":"process is finished."}, status=status.HTTP_200_OK)

                    request.session[f'lst_pos_process_{pk}'] = curr_pos

                ResponseFormHistory.objects.create(
                    user=request.user,
                    form=form
                )

                answer_data = {
                    'user': request.user.username,
                    'response': responses, 
                }
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'form_{form_id}', 
                    {
                        'type': 'send_answer',
                        'answer_data': answer_data
                    }
                )

                return response.Response(
                    {"detail": "The answers were successfully registered"}, 
                    status=status.HTTP_200_OK
                )

            return response.Response({}, status=status.HTTP_400_BAD_REQUEST)


        if request.method == "GET":
            if not process_instance.is_public():
                pass_cash = request.session.get(f'verified_process_{pk}', "")
                if pass_cash != process_instance.password:
                    return response.Response({"detail": "Incorrect password. Submit the correct password!"}, status=status.HTTP_403_FORBIDDEN)

            if form_id is None:
                form_id = 1

            if process_instance.type == "linear":
                form_id = request.session.get(f'lst_pos_process_{pk}',0) + 1
                curr_position = get_object_or_404(FormPosition,Q(process=process_instance)&Q(position=form_id))
                form = curr_position.form
            else:
                forms = process_instance.forms.all()
                try:
                    form = forms.get(id=form_id)
                except:
                    return response.Response({"detail": "this form dose not exist!"}, status=status.HTTP_404_NOT_FOUND)

            questions = form.questions.all()
            serializer = QuestionSerializer(questions, many=True)

            WatchFormHistory.objects.create(
                user=request.user,
                form=form
            )

            return response.Response(serializer.data, status=status.HTTP_200_OK)



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


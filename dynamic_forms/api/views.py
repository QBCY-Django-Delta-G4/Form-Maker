from rest_framework import viewsets
from dynamic_forms.models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken




# class FormListView(generics.ListAPIView):
#     queryset = Form.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = FormSerializer




class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer



# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")

#         user = authenticate(username=username, password=password)

#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             access_token = str(refresh.access_token)
#             refresh_token = str(refresh)

#             return Response({
#                 'access': access_token,
#                 'refresh': refresh_token
#             }, status=status.HTTP_200_OK)

#         return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


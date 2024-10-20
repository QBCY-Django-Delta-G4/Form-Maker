from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .viewsets import *


router = DefaultRouter()
router.register(r'forms/manage', ManageFormViewSet, basename='forms-manage')
router.register(r'process/manage', ManageProcessViewSet, basename='process-manage')
router.register(r'process', ProcessListViewSet, basename='process-list')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('register/', UserRegistrationView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='token_obtain_pair'),


]
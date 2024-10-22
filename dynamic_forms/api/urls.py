from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .viewsets import *


router = DefaultRouter()
router.register(r'manage/category', ManageCategoryViewSet, basename='category')
router.register(r'manage/process', ManageProcessViewSet, basename='process-manage')
router.register(r'manage/form', ManageFormViewSet, basename='form')
router.register(r'manage/question', ManageQuestionViewSet, basename='question')
# router.register(r'form-position', FormPositionListViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'process', ProcessListViewSet, basename='process-list')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('register/', UserRegistrationView.as_view(), name='register'),

    path('login/', LoginView.as_view(), name='token_obtain_pair'),


]
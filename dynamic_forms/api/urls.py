from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'forms', FormViewSet, basename='forms')
router.register(r'process', ProcessViewSet, basename='process')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'select-choice', SelectChoiceViewSet, basename='select-choice')
router.register(r'responses', ResponseViewSet, basename='response')
router.register(r'watch-form-history', WatchFormHistoryViewSet, basename='watch-form-history')


urlpatterns = [
    path('', include(router.urls)),
]
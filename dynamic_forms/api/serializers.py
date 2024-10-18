from rest_framework import serializers
from dynamic_forms.models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'owner', 'name']


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['id', 'owner', 'title', 'position']


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'owner', 'title', 'category', 'forms', 'type', 'is_public', 'password']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'form', 'title', 'type']


class SelectChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectChoice
        fields = ['id', 'select_question', 'title']


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['id', 'user', 'question', 'answer']


class WatchFormHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchFormHistory
        fields = ['id', 'user', 'form', 'watched_at']
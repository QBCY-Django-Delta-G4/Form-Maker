from rest_framework import serializers
from dynamic_forms.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'owner', 'name']

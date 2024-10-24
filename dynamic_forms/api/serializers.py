from rest_framework import serializers
from dynamic_forms.models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken  




class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'url']

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({'username': 'Username already taken.'})
        return value

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({'email': 'Email already taken.'})
        return value



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'owner', 'name']
        read_only_fields = ['owner',]



class FormSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Form
        fields = [
            'id', 'owner', 'owner_username', 'title',
            'category', 'category_name',
            'is_public', 'password'
        ]
        read_only_fields = ['owner',]



class FormPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormPosition
        fields = ['id', 'process', 'form', 'position']
        # read_only_fields = ['form', 'process']



class ProcessListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Process
        fields = [
            'id',
            'owner_username', 
            'title',
            'category_name',
            'forms', 'type',
            'is_public',
        ]



class ProcessSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    forms = serializers.PrimaryKeyRelatedField(many=True, queryset=Form.objects.none())

    class Meta:
        model = Process
        fields = [
            'id',
            'owner', 'owner_username', 
            'title',
            'category', 'category_name',
            'forms', 'type',
            'is_public', 'password',
            'positions',
        ]
        read_only_fields = ['owner', 'positions']

    def create(self, validated_data):
        forms = validated_data.pop('forms')
        data = self.data
        process = Process.objects.create(**validated_data)
        forms = list(dict.fromkeys(forms))
        for position, form in enumerate(forms):
            process.forms.add(form)
            if process.type == "linear":
                FormPosition.objects.create(process=process,form=form,position=position+1)
        return process

    def update(self, instance:Process, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.category = validated_data.get('category', instance.category)
        instance.password = validated_data.get('password', instance.password)

        type = validated_data.get('type', None)
        forms = validated_data.get('forms', None)
        if type is not None  and  type != instance.type:
            instance.type = type
            if forms is None:
                FormPosition.objects.filter(process=instance).delete()
                if type == "linear":
                    for position, form in enumerate(instance.forms.all()):
                        FormPosition.objects.create(process=instance,form=form,position=position+1)

        if forms is not None:
            forms = validated_data.pop('forms')
            instance.forms.clear()
            FormPosition.objects.filter(process=instance).delete()
            forms = list(dict.fromkeys(forms))
            for position, form in enumerate(forms):
                instance.forms.add(form)
                if instance.type == "linear":
                    FormPosition.objects.create(process=instance,form=form,position=position+1)

        instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        user = kwargs['context']['request'].user
        super(ProcessSerializer, self).__init__(*args, **kwargs)
        self.fields['forms'].child_relation.queryset = Form.objects.filter(owner=user)



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'form', 'title', 'type', 'extra']
        read_only_fields = ['form',]
        # extra_kwargs = {
        #     'url': {'view_name':'question-detail'}
        # }



class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError({'username': 'Username already taken.'})
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({'email': 'Email already taken.'})
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password1'])  # Hash the password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError("Invalid login credentials.")
        else:
            raise serializers.ValidationError("Must provide both username and password.")
        
        data['user'] = user  # Store the authenticated user in the validated data
        return data

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)  # Generate JWT token for the authenticated user
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    pass




class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categorys")
    name  = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name + " - " + self.owner.username


class Form(models.Model):
    owner  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_forms")
    title  = models.CharField(max_length=255)
    password = models.CharField(max_length=255, null=True, blank=True)

    def is_public(self):
        return self.password is None or self.password == ""

    def __str__(self) -> str:
        return self.title + " - " + self.owner.username


class Process_Type(models.TextChoices):
    LINEAR = 'linear'
    FREE = 'free'

class Process(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_process")
    title  = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True,
        related_name="category_process"
    )
    forms = models.ManyToManyField("Form", related_name="form_process")
    type = models.CharField(max_length=10, choices=Process_Type.choices, default=Process_Type.FREE)
    password = models.CharField(max_length=255, null=True, blank=True)

    def is_public(self):
        return self.password is None or self.password == ""

    def __str__(self) -> str:
        return self.title + " - " + self.owner.username


class FormPosition(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('process', 'position')


class Question(models.Model):
    class Question_Type(models.TextChoices):
        TEXT = 'text'
        SELECT = 'select'
        CHECKBOX = 'checkbox'

    form  = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
    title = models.TextField()
    type  = models.CharField(max_length=10, choices=Question_Type.choices, default=Question_Type.TEXT)
    extra = models.JSONField()

    def __str__(self) -> str:
        return self.title + " - " + self.form.__str__()


class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_responses')
    answer = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.question.title + " - " + self.user.username


class WatchFormHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_watch_histories')
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='form_watch_histories')
    watched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.form.title + " - " + self.user.username


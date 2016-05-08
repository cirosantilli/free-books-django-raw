from django.contrib.auth.models import User
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=256)
    body = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

# class Tag(models.Model):

# class QuestionsTags(models.Model):

# class Profile(models.Model):

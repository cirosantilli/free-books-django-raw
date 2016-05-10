# TODO think about timezones.

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import ModelForm

class Article(models.Model):
    body = models.TextField(max_length=256)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    last_edited = models.DateTimeField(auto_now_add=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)
    title = models.CharField(max_length=256)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id)])
    # TODO enforce non-empty title and body here, currently only done for GUI.
    # Then write test for it.

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'body']

# class Tag(models.Model):

# class QuestionsTags(models.Model):

# class Profile(models.Model):

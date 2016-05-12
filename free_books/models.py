# TODO think about timezones.

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm

class Article(models.Model):
    body = models.TextField()
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

class Profile(models.Model):
    about = models.TextField()
    last_edited = models.DateTimeField(auto_now_add=True, blank=True)
    reputation = models.BigIntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username
    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])
    @property
    def real_name(self):
        return self.user.first_name + ' ' + self.user.last_name

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['about']

def create_profile(sender, instance, created, **kwargs):
    if created:
       Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)

# class Tag(models.Model):

# class QuestionsTags(models.Model):

# class Profile(models.Model):

# TODO think about timezones.

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm

# Remove colon from labels
# http://stackoverflow.com/a/11622672/895245
class MyModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

class Profile(models.Model):
    about = models.TextField()
    last_edited = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='profile last edited')
    # This is just a cache, but definitely required as it is an expensive value to calculate.
    linear_reputation = models.BigIntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username
    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])
    @property
    def real_name(self):
        return self.user.first_name + ' ' + self.user.last_name
    def has_upvoted(self, article):
        return ArticleVote.objects.filter(
                article=article,
                type=ArticleVote.LIKE,
                user=self.user,
                value=ArticleVote.UPVOTE).exists()
    def has_downvoted(self, article):
        return ArticleVote.objects.filter(
                article=article,
                type=ArticleVote.LIKE,
                user=self.user,
                value=ArticleVote.DOWNVOTE).exists()

class UserForm(MyModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ProfileForm(MyModelForm):
    class Meta:
        model = Profile
        fields = ['about']

def create_profile(sender, instance, created, **kwargs):
    if created:
       Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)

class Article(models.Model):
    body = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_creator')
    last_edited = models.DateTimeField(auto_now_add=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    title = models.CharField(max_length=256)
    votes = models.ManyToManyField(User, through='ArticleVote', related_name='article_votes')
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id)])
    def upvote_count(self):
        return ArticleVote.objects.filter(article=self, type=ArticleVote.LIKE, value=ArticleVote.UPVOTE).count()
    def downvote_count(self):
        return ArticleVote.objects.filter(article=self, type=ArticleVote.LIKE, value=ArticleVote.DOWNVOTE).count()
    def net_votes(self):
        return self.upvote_count() - self.downvote_count()
    # TODO enforce non-empty title and body here, currently only done for GUI.
    # Then write test for it.

class ArticleForm(MyModelForm):
    class Meta:
        model = Article
        fields = ['title', 'body']

class ArticleVote(models.Model):
    LIKE = 0
    TYPE_CHOICES = (
        (LIKE, 'Like'),
    )
    UPVOTE = 0
    DOWNVOTE = 1
    VALUE_CHOICES = (
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    )
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    type = models.IntegerField(choices=TYPE_CHOICES, default=UPVOTE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(choices=VALUE_CHOICES, default=UPVOTE)
    class Meta:
        unique_together = ('article', 'type', 'user')

class ArticleVoteForm(MyModelForm):
    class Meta:
        model = ArticleVote
        fields = ['article', 'type', 'user', 'value']

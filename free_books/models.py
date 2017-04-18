# TODO think about timezones.

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, Count, When, Sum
from django.db.models.signals import post_save
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # This could be used to cache reputation queries.
    # linear_reputation = models.BigIntegerField(default=0)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])

    @property
    def real_name(self):
        return self.user.first_name + ' ' + self.user.last_name

    def has_upvoted(self, article):
        """
        True if use has upvoted a given article, false otherwise.
        """
        return ArticleVote.objects.filter(
                article=article,
                creator=self.user,
                type=ArticleVote.LIKE,
                value=ArticleVote.UPVOTE).exists()

    def has_downvoted(self, article):
        """
        True if use has downvoted a given article, false otherwise.
        """
        return ArticleVote.objects.filter(
                article=article,
                creator=self.user,
                type=ArticleVote.LIKE,
                value=ArticleVote.DOWNVOTE).exists()

    @property
    def article_votes_cast_count(self):
        return ArticleVote.objects.filter(creator=self.user,
                type=ArticleVote.LIKE).count()

    @property
    def article_upvotes_cast_count(self):
        return ArticleVote.objects.filter(creator=self.user,
                type=ArticleVote.LIKE, value=ArticleVote.UPVOTE).count()

    @property
    def article_downvotes_cast_count(self):
        return ArticleVote.objects.filter(creator=self.user,
                type=ArticleVote.LIKE, value=ArticleVote.DOWNVOTE).count()

    @property
    def article_votes_received_count(self):
        return ArticleVote.objects.filter(article__creator=self.user,
                                          type=ArticleVote.LIKE).count()

    @property
    def article_upvotes_received_count(self):
        return ArticleVote.objects.filter(article__creator=self.user,
                type=ArticleVote.LIKE, value=ArticleVote.UPVOTE).count()

    @property
    def article_downvotes_received_count(self):
        return ArticleVote.objects.filter(article__creator=self.user,
                type=ArticleVote.LIKE, value=ArticleVote.DOWNVOTE).count()

    @property
    def linear_reputation(self):
        return ArticleVote.objects.filter(
                              article__creator=self.user,
                              type=ArticleVote.LIKE) \
                          .aggregate(Sum('value'))['value__sum']

    @classmethod
    def get_users_with_most_linear_reputation(cls):
        return User.objects.filter(article__articlevote__type=ArticleVote.LIKE) \
                        .annotate(linear_reputation=Sum('article__articlevote__value')) \
                        .order_by('-linear_reputation')

class UserForm(MyModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ProfileForm(MyModelForm):
    class Meta:
        model = Profile
        fields = ['about']

def createProfile(sender, instance, created, **kwargs):
    if created:
       Profile.objects.create(user=instance)

post_save.connect(createProfile, sender=User)

class Article(models.Model):

    body = models.TextField(max_length=1048576, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    last_edited = models.DateTimeField(auto_now_add=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    title = models.CharField(max_length=256)

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

    @classmethod
    def get_articles_with_most_net_votes(cls, articles=None):
        if articles is None:
            articles = cls.objects
        else:
            articles = Article.objects.filter(pk__in=articles)
        return articles.annotate(net_votes=Sum(Case(
            When(
                articlevote__type=ArticleVote.LIKE,
                then='articlevote__value'
            ),
            default=0
        ))).order_by('-net_votes')

    @classmethod
    def filter_with_at_least_one_defined_tag_upvote(cls, articles, tag_name, user_downvote_remove=None):
        """
        -   user_downvote_remove: if this user has downvoted a tag for an article,
            remove that article from the retuned list, regardless of what other users have voted.
        """
        annotate_kwargs = {
            'tag_upvote_count':Count(Case(When(
                    articletagvote__defined_by_article=True,
                    articletagvote__name=tag_name,
                    articletagvote__value=ArticleTagVote.UPVOTE,
                    then=True,
                ),
                default=None
            ))
        }
        filter_kwargs = {'tag_upvote_count__gt':0}
        if user_downvote_remove is not None:
            annotate_kwargs['tag_user_downvote_count'] = Count(Case(When(
                articletagvote__creator=user_downvote_remove,
                articletagvote__defined_by_article=True,
                articletagvote__name=tag_name,
                articletagvote__value=ArticleTagVote.DOWNVOTE,
                then=True,
                ),
                default=None
            ))
            filter_kwargs['tag_user_downvote_count'] = 0
        return articles.annotate(**annotate_kwargs).filter(**filter_kwargs)

class ArticleForm(MyModelForm):
    class Meta:
        model = Article
        fields = ['title', 'body']

class ArticleVote(models.Model):
    class Meta:
        unique_together = ('article', 'creator', 'type')
    LIKE = 0
    TYPE_CHOICES = (
        (LIKE, 'Like'),
    )
    # Use 1 and -1 so that we can do a SUM() to get the net value.
    UPVOTE = 1
    DOWNVOTE = -1
    VALUE_CHOICES = (
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    )
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    # We might add more types later on, like flagging illegal content.
    type = models.IntegerField(choices=TYPE_CHOICES, default=UPVOTE)
    value = models.IntegerField(choices=VALUE_CHOICES, default=UPVOTE)

# Something along those lines would be needed if we were to cache the linear reputation on a column.
# Considerations:
# - UPDATE must be atomic: http://stackoverflow.com/questions/1598932/atomic-increment-of-a-counter-in-django
# - must use pre_save to see how values changed up / down:
#     http://stackoverflow.com/questions/5582410/django-how-to-access-original-unmodified-instance-in-post-save-signal
# Maybe another option is to use Redis or memcached?
#def updateLinearReputation(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.get(instance.article.creator).update(
#                linear_reputation=(F('linear_reputation') + 1))
#pre_save.connect(createArticleVote, sender=ArticleVote)
#def deleteLinearReputation(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.get(instance.article.creator).update(
#                linear_reputation=(F('linear_reputation') + 1))
#post_save.connect(createArticleVote, sender=ArticleVote)

class ArticleVoteForm(MyModelForm):
    class Meta:
        model = ArticleVote
        fields = ['article', 'creator', 'type', 'value']

# TODO do we need to translate this message?
article_tag_vote_regex = '[0-9a-z-]+'
alphanumeric_lower_hyphen_validator = RegexValidator(
    r'^' + article_tag_vote_regex + '$',
    _('Only lowercase letters "a-z", digits "0-9" and hyphens "-" are allowed.')
)
class ArticleTagVote(models.Model):
    class Meta:
        unique_together = ('article', 'creator', 'defined_by_article', 'name')
    UPVOTE = 1
    DOWNVOTE = -1
    VALUE_CHOICES = (
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    )
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    defined_by_article = models.BooleanField(default=True)
    # TODO name restrictions. [0-9a-z-].
    name = models.CharField(max_length=256, validators=[alphanumeric_lower_hyphen_validator])
    value = models.IntegerField(choices=VALUE_CHOICES, default=UPVOTE)

    @classmethod
    def get_tag_name_regex(cls):
        return article_tag_vote_regex

    @classmethod
    def get_unique_tag_upvotes(cls):
        return cls.objects \
            .filter(value=cls.UPVOTE, defined_by_article=True) \
            .values('name') \
            .annotate(
                upvote_count=Count('article'),
                article_count=Count('article', distinct=True),
                user_count=Count('creator', distinct=True),
            )

class ArticleTagVoteForm(MyModelForm):
    class Meta:
        model = ArticleTagVote
        fields = ['article', 'creator', 'defined_by_article', 'name', 'value']

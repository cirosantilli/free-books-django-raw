"""
Generate a non-faked deterministic dataset. Good for initial debugging.

TODO: take the 10 first users, articles, etc. and make them denser.
Doing dense things for all users takes too long, but it is good to have some dense relations as well.
"""

import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from free_books.models import Article, Profile, ArticleTagVote, ArticleVote

"""
TODO Also reset the ID counter to 0.

Or find a way to get the ide of bulk created obejcts.

Right now, we need to completey delete the database and migrate,
which takes some seconds.

./manage.py flush does not reset the index either.

https://docs.djangoproject.com/en/1.9/ref/django-admin/#sqlsequencereset
could be used but is a pain as you need one call per app.

TRUNCATE would work as well, but it is not possible to do it:
http://stackoverflow.com/questions/2988997/how-do-i-truncate-table-using-django-orm
"""
# User.objects.all().delete()

nusers = 100
narticles = nusers * 10
votes_per_user = 9
total_tag_names = 10
max_tags_per_article = 50

def users_iterator():
    for i in range(nusers):
        n = i + 1
        is_superuser = (n == 1)
        user = User(
            first_name='First' + str(n),
            is_staff=is_superuser,
            is_superuser=is_superuser,
            last_name='Last' + str(n),
            username='user' + str(n),
        )
        user.set_password('asdfqwer')
        yield user

def profiles_iterator():
    for i in range(nusers):
        n = i + 1
        yield Profile(
            about='About ' + str(n),
            user_id=n
        )

def articles_iterator():
    for i in range(narticles):
        n = i + 1
        yield Article(
            body='Body ' + str(n),
            title='Title ' + str(n),
            creator_id=(1 + (i % nusers))
        )

def article_votes_iterator():
    for user_pk in range(1, nusers + 1):
        nvotes = 0
        article_pk = 1
        while nvotes < votes_per_user:
            if (nvotes % 5) == 0:
                value = ArticleVote.DOWNVOTE
            else:
                value = ArticleVote.UPVOTE
            yield ArticleVote(
                article_id=article_pk,
                creator_id=user_pk,
                type=ArticleVote.LIKE,
                value=value,
            )
            nvotes += 1
            article_pk = 1 + ((nvotes * user_pk) % narticles)

def article_tag_votes_iterator():
    for article_pk in range(1, narticles + 1):
        ntags = 0
        tags_per_article = int(max_tags_per_article * 2**(-ntags))
        while ntags < tags_per_article:
            if (ntags % 5) == 0:
                value = ArticleTagVote.DOWNVOTE
            else:
                value = ArticleTagVote.UPVOTE
            yield ArticleTagVote(
                article_id=article_pk,
                creator_id=((ntags % nusers) + 1),
                defined_by_article=((ntags % 3) == 0),
                name='tag' + str(ntags % total_tag_names),
                value=value,
            )
            ntags += 1

def article_tag_votes_creator_iterator():
        """
        have some tags by article creators.
        """
        ntags = 0
        for article_pk in range(1, narticles + 1):
            # TODO DRY up this check further.
            article_pk_mod = article_pk % 5
            if article_pk_mod != 0:
                creator_pk = Article.objects.get(pk=article_pk).creator.pk
                name = 'tag' + str(ntags % total_tag_names)
                params = {
                    'article_id':article_pk,
                    'creator_id':creator_pk,
                    'defined_by_article':(article_pk_mod != 4),
                    'name':name,
                }
                if not (ArticleTagVote.objects.filter(**params)):
                    params.update({'value':ArticleTagVote.UPVOTE})
                    vote = ArticleTagVote(**params)
                    yield vote
                ntags += 1

class Command(BaseCommand):
    def handle(self, **options):

        print('users')
        time = datetime.datetime.now()
        User.objects.bulk_create(iter(users_iterator()))
        print(datetime.datetime.now() - time)
        print()

        print('profiles')
        time = datetime.datetime.now()
        Profile.objects.bulk_create(iter(profiles_iterator()))
        print(datetime.datetime.now() - time)
        print()

        print('articles')
        time = datetime.datetime.now()
        Article.objects.bulk_create(iter(articles_iterator()))
        print(datetime.datetime.now() - time)
        print()

        print('article votes')
        time = datetime.datetime.now()
        ArticleVote.objects.bulk_create(iter(article_votes_iterator()))
        print(datetime.datetime.now() - time)
        print()

        print('article tag votes')
        time = datetime.datetime.now()
        ArticleTagVote.objects.bulk_create(iter(article_tag_votes_iterator()))
        print(datetime.datetime.now() - time)
        print()

        print('article tag votes creator')
        time = datetime.datetime.now()
        ArticleTagVote.objects.bulk_create(iter(article_tag_votes_creator_iterator()))
        print(datetime.datetime.now() - time)
        print()

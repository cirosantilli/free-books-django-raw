from django.core.management.base import BaseCommand

from free_books.models import Article, Profile
from django.contrib.auth.models import User

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
            reputation=(n * 10),
            user=User.objects.get(pk=n)
        )

def articles_iterator():
    for i in range(narticles):
        n = i + 1
        yield Article(
            body='Body ' + str(n),
            title='Title ' + str(n),
            creator=User.objects.get(pk=(1 + (i % nusers)))
        )

class Command(BaseCommand):
    def handle(self, **options):
        User.objects.bulk_create(iter(users_iterator()))
        Profile.objects.bulk_create(iter(profiles_iterator()))
        Article.objects.bulk_create(iter(articles_iterator()))

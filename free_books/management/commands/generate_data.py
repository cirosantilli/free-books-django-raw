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
        is_superuser = (i == 0)
        user = User(
            first_name='First' + str(i),
            is_staff=is_superuser,
            is_superuser=is_superuser,
            last_name='Last' + str(i),
            username='user' + str(i),
        )
        user.set_password('asdfqwer')
        yield user

def profiles_iterator():
    for i in range(nusers):
        yield Profile(
            about='About +' + str(i),
            reputation=i * 10,
            user=User.objects.get(pk=i + 1)
        )

class Command(BaseCommand):
    def handle(self, **options):
        User.objects.bulk_create(iter(users_iterator()))
        Profile.objects.bulk_create(iter(profiles_iterator()))

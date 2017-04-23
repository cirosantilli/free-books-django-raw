# Free Books Raw Django

<https://githiub.com/cirosantilli/write-free-science-books-to-get-famous-website> **early** prototype using raw Django as base, i.e. no pre-made Django site.

This is no more than a blog sub sub set now, but it will one day topple Wikipedia, Stack Overflow, Quora, Springer, <https://del.icio.us/> and the educational system all at once. Lol.

## Getting started

How to run it:

    sudo apt-get intall postgresql libpq-dev
    sudo pip install --upgrade virtualenv
    virtualenv -p python3.5 .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    # TODO drop / truncate database if one exists.
    # Find a better method (more portable and faster)
    # http://stackoverflow.com/questions/3414247/django-drop-all-tables-from-database
    rm -f db.sqlite3
    python manage.py generate_data
    Ipython manage.py runserver
    firefox localhost:8000

Now login with:

- username: `user0` for an admin, or `user{1-100}` for non-admins
- password: `asdfqwer` for everyone

Tested on Ubuntu 16.04, Python 3.5.

## About

This is basically a simple multi-user blog.

We could consider using existing Django libraries as a basis, e.g.: <https://www.djangopackages.com/grids/g/blogs/>

But yeah, if you can't make a blog app, you can't make any app.

And those blog apps have many blog-specific features which we don't need, which adds time to find the ones that matter.

## Heroku deployment

Initial deployment:

    APP_NAME='cirosantilli-free-books'
    DEMO_SERVER=false
    heroku login
    heroku create "$APP_NAME"
    heroku addons:create heroku-postgresql:hobby-dev
    git push heroku master
    if $DEMO_SERVER; then
        heroku pg:reset DATABASE_URL
        heroku run python manage.py generate_data
    else
        heroku run python manage.py migrate
    fi
    firefox "https://${APP_NAME}.herokuapps.com"

Update:

    git push heroku master
    if $DEMO_SERVER; then
        heroku pg:reset DATABASE_URL
        heroku run python manage.py generate_data
    else
        heroku run python manage.py migrate
    fi
    heroku run python manage.py migrate

Free tier limits:

- 10k database rows

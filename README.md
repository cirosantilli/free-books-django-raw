# Free Books Raw Django

<https://githiub.com/cirosantilli/write-free-science-books-to-get-famous-website> **early** prototype using raw Django as base, i.e. no pre-made Django site.

How to run it: <https://github.com/cirosantilli/django-cheat2/blob/1c1dfcee6c27d483def5b6a1e873c4fc63886fba/getting-started.md>

Tested on Ubuntu 16.04, Python 3.5.

This is basically a simple multi-user blog.

We could consider using existing Django libraries as a basis, e.g.: <https://www.djangopackages.com/grids/g/blogs/>

But yeah, if you can't make a blog app, you can't make any app.

And those blog apps have many blog-specific features which we don't need, which adds time to find the ones that matter.

## Heroku deployment

    APP_NAME='cirosantilli-free-books'
    sudo apt-get intall postgresql libpq-dev
    heroku login
    heroku create "$APP_NAME"
    heroku addons:create heroku-postgresql:hobby-dev
    git push heroku master
    # TODO drop / truncate database if one exists.
    heroku run python manage.py migrate
    heroku run python manage.py generate_data
    firefox "http://${APP_NAME}.herokuapps.com"

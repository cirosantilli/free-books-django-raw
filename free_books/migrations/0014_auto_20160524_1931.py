# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-24 19:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('free_books', '0013_auto_20160523_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('defined_by_article', models.BooleanField(verbose_name=True)),
                ('slug', models.CharField(max_length=256)),
                ('value', models.IntegerField(choices=[(1, 'Upvote'), (-1, 'Downvote')], default=1)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='free_books.Article')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='articletag',
            unique_together=set([('article', 'creator', 'defined_by_article', 'slug')]),
        ),
    ]

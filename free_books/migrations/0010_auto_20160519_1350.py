# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-19 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('free_books', '0009_auto_20160515_2135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='linear_reputation',
        ),
        migrations.AlterField(
            model_name='article',
            name='body',
            field=models.TextField(max_length=1048576),
        ),
    ]
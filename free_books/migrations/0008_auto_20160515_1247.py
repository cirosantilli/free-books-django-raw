# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-15 12:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('free_books', '0007_auto_20160515_1144'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='reputation',
            new_name='linear_reputation',
        ),
    ]

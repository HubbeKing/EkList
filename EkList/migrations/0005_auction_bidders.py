# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-03 20:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('EkList', '0004_auto_20161103_0009'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='bidders',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]

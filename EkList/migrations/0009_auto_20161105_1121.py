# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-05 09:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EkList', '0008_auto_20161105_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='bidders',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='auction',
            name='modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-05 09:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EkList', '0006_remove_auction_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='bidders',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='auction',
            name='current_bid',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='auction',
            name='current_bid_timestamp',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='current_bidder_username',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='auction',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='auction',
            name='modified',
            field=models.DateTimeField(blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-02 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EkList', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='creator_id',
        ),
        migrations.RemoveField(
            model_name='auction',
            name='current_bidder_id',
        ),
        migrations.AddField(
            model_name='auction',
            name='creator_username',
            field=models.CharField(default='anon', max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auction',
            name='current_bidder_username',
            field=models.CharField(default='anon', max_length=64),
            preserve_default=False,
        ),
    ]

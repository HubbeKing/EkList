# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-02 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('description', models.TextField()),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
                ('version', models.PositiveIntegerField()),
                ('creator_id', models.PositiveIntegerField()),
                ('expires', models.DateTimeField()),
                ('current_bid', models.FloatField()),
                ('current_bidder_id', models.PositiveIntegerField()),
                ('current_bid_timestamp', models.DateTimeField()),
                ('is_banned', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('preferred_language', models.CharField(max_length=8)),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-02 22:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EkList', '0003_auction_minimum_bid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auction',
            options={'permissions': (('ban_auction', 'Can ban any auction'),)},
        ),
    ]

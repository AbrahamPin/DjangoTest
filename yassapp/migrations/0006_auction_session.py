# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-25 12:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yassapp', '0005_auction_bidder'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='session',
            field=models.CharField(default='', max_length=64),
        ),
    ]
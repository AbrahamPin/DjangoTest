# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-29 23:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yassapp', '0006_auto_20171030_0127'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction',
            old_name='start_time',
            new_name='deadline',
        ),
    ]

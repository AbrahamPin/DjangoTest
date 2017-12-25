# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-23 17:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('yassapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auction',
            options={},
        ),
        migrations.AddField(
            model_name='auction',
            name='activestatus',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='auction',
            name='banstatus',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auction',
            name='price',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=19),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='auction',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller', to=settings.AUTH_USER_MODEL),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2018-12-07 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sf', '0005_auto_20181207_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='pozycja',
            name='kontener',
            field=models.BooleanField(default=False),
        ),
    ]
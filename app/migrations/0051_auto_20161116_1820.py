# -*- coding: utf-8 -*-
# Generated by Django 1.9.11.dev20161013150334 on 2016-11-16 18:20
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0050_auto_20161018_1809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.6.dev20160421010813 on 2016-05-20 21:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_zlctxt'),
    ]

    operations = [
        migrations.AddField(
            model_name='plik',
            name='odkad',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Odkad'),
        ),
    ]

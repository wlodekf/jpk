# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-03-09 21:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0062_auto_20170218_2355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firma',
            name='oznaczenie',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
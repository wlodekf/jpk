# -*- coding: utf-8 -*-
# Generated by Django 1.9.11.dev20161013150334 on 2016-12-15 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0055_plik_firma'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firma',
            name='nazwa',
            field=models.CharField(max_length=100, verbose_name='Nazwa'),
        ),
    ]
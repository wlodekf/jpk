# -*- coding: utf-8 -*-
# Generated by Django 1.9.14.dev20170906233242 on 2020-02-28 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0076_auto_20200228_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='deklaracja',
            name='element',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Element'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.11.dev20161013150334 on 2017-01-28 21:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bra', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='faktura',
            name='nip_nabywcy',
            field=models.CharField(max_length=20, null=True),
        ),
    ]

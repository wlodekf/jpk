# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-03-13 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bra', '0013_auto_20170313_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='importsprzedazy',
            name='do_daty',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='importsprzedazy',
            name='od_daty',
            field=models.DateField(blank=True, null=True),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-03-11 12:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0063_auto_20170309_2100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firma',
            name='nr_lokalu',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Nr lokalu'),
        ),
    ]

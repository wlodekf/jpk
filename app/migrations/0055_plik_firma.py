# -*- coding: utf-8 -*-
# Generated by Django 1.9.11.dev20161013150334 on 2016-12-15 17:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0054_auto_20161215_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='plik',
            name='firma',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Firma'),
        ),
    ]

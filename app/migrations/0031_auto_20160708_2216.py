# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-07-08 22:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20160708_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='magkart',
            name='id_towar',
            field=models.ForeignKey(db_column='id_towar', on_delete=django.db.models.deletion.CASCADE, to='app.MagTowar'),
        ),
    ]

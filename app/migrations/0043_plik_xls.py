# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-08-10 12:54
from __future__ import unicode_literals

import app.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0042_blad'),
    ]

    operations = [
        migrations.AddField(
            model_name='plik',
            name='xls',
            field=app.model_fields.CompressedTextField(null=True, verbose_name='Plik kontrolny XLS'),
        ),
    ]

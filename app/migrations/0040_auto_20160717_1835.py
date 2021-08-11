# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-07-17 18:35
from __future__ import unicode_literals

import app.model_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_auto_20160716_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='plik',
            name='upo',
            field=app.model_fields.CompressedTextField(null=True, verbose_name='UPO'),
        ),
        migrations.AddField(
            model_name='plik',
            name='utworzony_user',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='status',
            name='user',
            field=models.CharField(default='wlodek', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storage',
            name='finish_user',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='init_user',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='put_user',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='storage',
            name='sign_user',
            field=models.CharField(default='wlodek', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storage',
            name='xades_user',
            field=models.CharField(max_length=10, null=True),
        ),
    ]

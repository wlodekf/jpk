# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-03-11 18:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0064_auto_20170311_1251'),
        ('bra', '0007_auto_20170311_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='faktura',
            name='firma',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='app.Firma'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='importsprzedazy',
            name='firma',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='app.Firma'),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-03-11 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bra', '0006_auto_20170311_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsprzedazy',
            name='faktury',
            field=models.FileField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='importsprzedazy',
            name='wiersze',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
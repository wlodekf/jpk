# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2018-12-10 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sf', '0009_auto_20181208_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='raport',
            name='tabela',
            field=models.CharField(max_length=20, null=True, verbose_name='Tabela'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-02-19 23:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polon', '0008_auto_20170219_1553'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tworzenie',
            options={'verbose_name': 'Generowanie faktur do PDF', 'verbose_name_plural': 'Informacja o generowaniu faktur do PDF'},
        ),
        migrations.AddField(
            model_name='tworzenie',
            name='grupowanie',
            field=models.CharField(default='tematy', max_length=10),
        ),
    ]

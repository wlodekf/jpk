# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-09-02 16:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0047_storage_bramka'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plik',
            name='kod',
            field=models.CharField(max_length=10, verbose_name=b'Kod pliku JPK'),
        ),
        migrations.AlterField(
            model_name='plik',
            name='stan',
            field=models.CharField(default=b'W KOLEJCE', max_length=15),
        ),
    ]

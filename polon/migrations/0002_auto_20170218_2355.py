# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-02-18 23:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polon', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tworzenie',
            name='zadanie',
        ),
        migrations.AddField(
            model_name='tworzenie',
            name='ktora',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tworzenie',
            name='stan',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tworzenie',
            name='ile_faktur',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tworzenie',
            name='rozmiar_zip',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='tworzenie',
            name='tmp_dir',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
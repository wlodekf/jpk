# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-07-11 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_auto_20160709_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plik',
            name='kod',
            field=models.CharField(choices=[(b'JPK_KR', 'Ksi\u0119gi rachunkowe'), (b'JPK_VAT', 'Rozliczenia VAT'), (b'JPK_FA', 'Faktury sprzeda\u017cy'), (b'JPK_WB', 'Wyci\u0105gi bankowe'), (b'JPK_MAG', 'Obr\xf3t magazynowy')], max_length=10, verbose_name=b'Kod pliku JPK'),
        ),
    ]

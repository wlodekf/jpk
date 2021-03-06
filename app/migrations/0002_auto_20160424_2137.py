# -*- coding: utf-8 -*-
# Generated by Django 1.9.6.dev20160421010813 on 2016-04-24 21:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paczka',
            name='cel',
            field=models.CharField(default='Kontrola', max_length=100, verbose_name='Cel kontroli'),
        ),
        migrations.AlterField(
            model_name='paczka',
            name='data',
            field=models.DateField(default=datetime.date.today, verbose_name='Data paczki'),
        ),
        migrations.AlterField(
            model_name='plik',
            name='czesc',
            field=models.CharField(blank=True, max_length=7, null=True, verbose_name='Miesiąc części'),
        ),
        migrations.AlterField(
            model_name='plik',
            name='kod',
            field=models.CharField(choices=[('JPK_KR', 'Księgi rachunkowe'), ('JPK_WB', 'Wyciągi bankowe'), ('JPK_VAT', 'Rozliczenia VAT'), ('JPK_FA', 'Faktury sprzedaży')], max_length=10, verbose_name='Kod pliku JPK'),
        ),
        migrations.AlterField(
            model_name='plik',
            name='utworzony',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Utworzony'),
        ),
    ]

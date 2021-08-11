# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2018-12-13 19:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sf', '0011_auto_20181213_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_gmina',
            field=models.CharField(max_length=36, null=True, verbose_name='Gmina'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_kod_pocztowy',
            field=models.CharField(max_length=8, null=True, verbose_name='Kod pocztowy'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_miejscowosc',
            field=models.CharField(max_length=56, null=True, verbose_name='Miejscowość'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_nazwa_firmy',
            field=models.CharField(max_length=255, null=True, verbose_name='Pełna nazwa firmy'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_nr_domu',
            field=models.CharField(max_length=9, null=True, verbose_name='Nr domu'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_pkd',
            field=models.CharField(max_length=100, null=True, verbose_name='Przedmiot działalności jednostki'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_poczta',
            field=models.CharField(max_length=56, null=True, verbose_name='Poczta'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_powiat',
            field=models.CharField(max_length=36, null=True, verbose_name='Powiat'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p1_wojewodztwo',
            field=models.CharField(max_length=36, null=True, verbose_name='Województwo'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p3_data_do',
            field=models.DateField(null=True, verbose_name='Koniec okresu'),
        ),
        migrations.AlterField(
            model_name='sprawozdanie',
            name='p3_data_od',
            field=models.DateField(null=True, verbose_name='Początek okresu'),
        ),
    ]
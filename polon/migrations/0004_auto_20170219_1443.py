# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-02-19 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polon', '0003_auto_20170219_0130'),
    ]

    operations = [
        migrations.AddField(
            model_name='faktura',
            name='zlc_sww',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='faktura',
            name='data_rozp',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='faktura',
            name='kon_nazwa',
            field=models.CharField(max_length=160, null=True),
        ),
        migrations.AlterField(
            model_name='faktura',
            name='opis',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='faktura',
            name='zamowienie',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='faktura',
            name='zlc_nazwa',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='faktura',
            name='zlc_tytul',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
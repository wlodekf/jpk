# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-02-19 15:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polon', '0006_faktura_opis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faktura',
            name='zlc_tytul',
        ),
        migrations.AlterField(
            model_name='faktura',
            name='zlc_nazwa',
            field=models.CharField(max_length=255, null=True),
        ),
    ]

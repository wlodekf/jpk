# -*- coding: utf-8 -*-
# Generated by Django 1.9.6.dev20160421010813 on 2016-04-28 20:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20160428_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='plik',
            name='task',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterModelTable(
            name='ksiopi',
            table='fk_ksiopi',
        ),
        migrations.AlterModelTable(
            name='uzy',
            table='fk_uzy',
        ),
    ]
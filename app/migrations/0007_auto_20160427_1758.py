# -*- coding: utf-8 -*-
# Generated by Django 1.9.6.dev20160421010813 on 2016-04-27 17:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20160427_1754'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ctrl',
            unique_together=set([('plik', 'tabela')]),
        ),
    ]
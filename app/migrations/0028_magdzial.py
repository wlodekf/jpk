# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-07-08 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20160617_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='MagDzial',
            fields=[
                ('rowid', models.IntegerField(primary_key=True, serialize=False)),
                ('dzial', models.CharField(max_length=3)),
                ('fk_kod', models.CharField(max_length=3, null=True)),
                ('nazwa', models.CharField(max_length=40, null=True)),
                ('typ_mag', models.CharField(max_length=1, null=True)),
                ('sprzedaz', models.CharField(max_length=1, null=True)),
            ],
            options={
                'ordering': ['dzial'],
                'db_table': 'mag_dzial',
                'managed': False,
            },
        ),
    ]

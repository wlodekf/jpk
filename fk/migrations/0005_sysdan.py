# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-02-15 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fk', '0004_magnumer'),
    ]

    operations = [
        migrations.CreateModel(
            name='SysDan',
            fields=[
                ('dan_id', models.AutoField(primary_key=True, serialize=False)),
                ('nr_uzy', models.CharField(max_length=10)),
                ('modul', models.CharField(max_length=3)),
                ('funkcja', models.CharField(max_length=3)),
                ('dane1', models.CharField(max_length=100)),
                ('dane2', models.CharField(max_length=100)),
                ('dane3', models.CharField(max_length=100)),
                ('dane4', models.CharField(max_length=100)),
                ('dane5', models.CharField(max_length=100)),
                ('dane6', models.CharField(max_length=100)),
                ('dane7', models.CharField(max_length=100)),
                ('dane8', models.CharField(max_length=100)),
                ('dane9', models.CharField(max_length=100)),
                ('dane0', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'sys_dan',
                'managed': False,
            },
        ),
    ]

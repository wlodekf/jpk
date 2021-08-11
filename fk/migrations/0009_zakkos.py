# -*- coding: utf-8 -*-
# Generated by Django 1.9.14.dev20170906233242 on 2020-05-06 12:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fk', '0008_defnum_fakzaf'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZakKos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('kwota', models.DecimalField(decimal_places=2, max_digits=16)),
                ('konto', models.CharField(max_length=20)),
                ('mpk', models.CharField(max_length=10)),
                ('zlecenie', models.CharField(max_length=10)),
                ('konto5', models.CharField(max_length=20)),
            ],
            options={
                'managed': False,
                'db_table': 'zak_kos',
            },
        ),
    ]

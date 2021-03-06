# -*- coding: utf-8 -*-
# Generated by Django 1.9.6.dev20160421010813 on 2016-04-27 21:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20160427_1912'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ksi',
            fields=[
                ('ksi_id', models.AutoField(primary_key=True, serialize=False)),
                ('nr_dowodu', models.CharField(max_length=10)),
                ('miesiac', models.CharField(max_length=7)),
                ('d_wyst', models.DateField()),
                ('d_ksieg', models.DateField()),
                ('d_kto', models.IntegerField()),
                ('konto', models.CharField(max_length=20)),
                ('strona', models.CharField(max_length=1)),
                ('kwota', models.DecimalField(decimal_places=2, max_digits=16)),
                ('opis', models.CharField(max_length=30, null=True)),
                ('data', models.DateField(null=True)),
                ('lp_dzi', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'fk_ksi',
                'managed': False,
            },
        ),
    ]

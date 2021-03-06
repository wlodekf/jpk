# -*- coding: utf-8 -*-
# Generated by Django 1.9.11.dev20161013150334 on 2016-12-18 17:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fk', '0002_kasdow_kaspoz'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZakPoz',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('p_netto', models.DecimalField(decimal_places=2, max_digits=16)),
                ('p_stawka', models.CharField(max_length=2)),
                ('p_vat', models.DecimalField(decimal_places=2, max_digits=16)),
                ('p_brutto', models.DecimalField(decimal_places=2, max_digits=16)),
                ('p_roz', models.CharField(max_length=3)),
                ('sww', models.CharField(max_length=10)),
                ('konto', models.CharField(max_length=20)),
                ('zlecenie', models.CharField(max_length=10)),
                ('konto5', models.CharField(max_length=20)),
                ('w_walucie', models.DecimalField(decimal_places=2, max_digits=16)),
            ],
            options={
                'db_table': 'zak_poz',
                'managed': False,
            },
        ),
    ]

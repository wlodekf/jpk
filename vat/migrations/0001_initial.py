# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2018-08-04 13:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KonVat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nip', models.CharField(max_length=20)),
                ('vat', models.CharField(max_length=1)),
                ('vat_data', models.DateField(default=datetime.date.today)),
            ],
            options={
                'db_table': 'kon_vat',
                'managed': False,
            },
        ),
    ]
